import os
import glob
import json
import time
import math
import pickle
import hashlib
import requests
from typing import List, Dict, Tuple

# =========================
# 基本設定
# =========================
OLLAMA_HOST = "http://localhost:11434"
GEN_MODEL_DEFAULT = "phi3"           # 生成モデル（任意のテキストモデル）
EMBED_CANDIDATES = [
    "nomic-embed-text",
    "mxbai-embed-large",
]  # 利用可能な埋め込みモデル候補（先に見つかった方を使う）

DATA_DIR = "./data"                  # .txtを置くフォルダ
INDEX_PATH = "./rag_index.pkl"       # ベクターインデックスの保存先
CHUNK_CHARS = 800                    # チャンク文字数
CHUNK_OVERLAP = 200                  # チャンクのオーバーラップ
TOP_K = 4                            # 検索で投げるコンテキスト数

# =========================
# 既存のシンプルな生成関数（ベースそのまま）
# =========================
def chat_ollama(prompt: str, model: str = GEN_MODEL_DEFAULT) -> str:
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    res_json = response.json()
    return res_json.get("response", "").strip()

# =========================
# 埋め込み（Embeddings API）
# =========================
def pick_embed_model() -> str:
    """候補の中で使える埋め込みモデルを返す。なければ例外。"""
    for m in EMBED_CANDIDATES:
        try:
            # 軽いダミーで叩いて確認
            _ = embed_texts(["ping"], m)
            return m
        except Exception:
            continue
    raise RuntimeError(
        f"有効な埋め込みモデルが見つかりません。先に `ollama pull {EMBED_CANDIDATES[0]}` 等を実行してください。"
    )

def embed_texts(texts: List[str], embed_model: str) -> List[List[float]]:
    """Ollama Embeddings APIでベクトル化"""
    vectors = []
    for t in texts:
        r = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": embed_model, "prompt": t},
            timeout=120,
        )
        r.raise_for_status()
        vectors.append(r.json()["embedding"])
    return vectors

# =========================
# データ読み込み & チャンク
# =========================
def read_txt_files(data_dir: str) -> List[Tuple[str, str]]:
    """(source_path, text) のリスト"""
    files = sorted(glob.glob(os.path.join(data_dir, "*.txt")))
    out = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                out.append((fp, f.read()))
        except UnicodeDecodeError:
            # ANSIなどの場合
            with open(fp, "r", encoding="cp932", errors="ignore") as f:
                out.append((fp, f.read()))
    return out

def chunk_text(text: str, size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
        if start >= n:
            break
    return chunks

# =========================
# ベクターインデックス
# =========================
def hash_corpus(files: List[Tuple[str, str]]) -> str:
    """コーパス変更検出用ハッシュ"""
    h = hashlib.sha256()
    for path, text in files:
        h.update(path.encode("utf-8"))
        h.update(str(os.path.getmtime(path)).encode("utf-8"))
        h.update(str(len(text)).encode("utf-8"))
    return h.hexdigest()

def build_or_load_index(
    data_dir: str = DATA_DIR,
    index_path: str = INDEX_PATH,
) -> Dict:
    """./data/*.txt からインデックスを構築 or 読み込み"""
    files = read_txt_files(data_dir)
    corpus_sig = hash_corpus(files)

    # 既存インデックスがあり、署名一致ならロード
    if os.path.exists(index_path):
        try:
            with open(index_path, "rb") as f:
                idx = pickle.load(f)
            if idx.get("corpus_sig") == corpus_sig:
                return idx
        except Exception:
            pass

    # 構築
    embed_model = pick_embed_model()
    chunks = []
    meta = []
    for path, text in files:
        for c in chunk_text(text, CHUNK_CHARS, CHUNK_OVERLAP):
            if c.strip():
                chunks.append(c)
                meta.append({"source": path})

    if not chunks:
        raise RuntimeError(f"{data_dir} にテキストが見つかりませんでした。")

    print(f"[RAG] チャンク数: {len(chunks)} / 埋め込み計算中…")
    embeddings = embed_texts(chunks, embed_model)

    index = {
        "corpus_sig": corpus_sig,
        "embed_model": embed_model,
        "chunks": chunks,
        "metas": meta,          # 各chunkの {source}
        "embeddings": embeddings,
        "built_at": time.time(),
    }
    with open(index_path, "wb") as f:
        pickle.dump(index, f)
    print(f"[RAG] インデックス作成完了 → {index_path}")
    return index

def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)

def retrieve(index: Dict, query: str, top_k: int = TOP_K) -> List[Tuple[float, str, str]]:
    """クエリに近いチャンクTopKを返す [(score, chunk, source), ...]"""
    qv = embed_texts([query], index["embed_model"])[0]
    scores = []
    for vec, chunk, meta in zip(index["embeddings"], index["chunks"], index["metas"]):
        s = cosine(qv, vec)
        scores.append((s, chunk, meta["source"]))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]

# =========================
# RAG用プロンプト生成 & 実行
# =========================
def build_prompt_with_context(user_query: str, contexts: List[Tuple[float, str, str]]) -> str:
    """コンテキストを結合してプロンプト化"""
    ctx_blocks = []
    for i, (_score, chunk, src) in enumerate(contexts, 1):
        ctx_blocks.append(f"[{i}] Source: {os.path.basename(src)}\n{chunk.strip()}")
    ctx_text = "\n\n---\n\n".join(ctx_blocks)

    prompt = f"""You are a retrieval-augmented assistant.
Use ONLY the provided context to answer the user's question. If the answer is not present in the context, say you don't know in Japanese.

# Context
{ctx_text}

# User Question (Japanese)
{user_query}

# Answer in Japanese (cite sources like [1], [2] if used):
"""
    return prompt

def rag_answer(user_query: str, gen_model: str = GEN_MODEL_DEFAULT) -> Tuple[str, List[Tuple[float, str, str]]]:
    index = build_or_load_index(DATA_DIR, INDEX_PATH)
    hits = retrieve(index, user_query, TOP_K)
    prompt = build_prompt_with_context(user_query, hits)
    answer = chat_ollama(prompt, model=gen_model)
    return answer, hits

# =========================
# CLI
# =========================
if __name__ == "__main__":
    # 対話プロンプト：RAGで回答
    try:
        while True:
            prompt = input("ユーザー: ").strip()
            if not prompt:
                continue
            if prompt.lower() in {"exit", "quit"}:
                break
            answer, hits = rag_answer(prompt, gen_model=GEN_MODEL_DEFAULT)
            print("\nAI:", answer)
            # 参考に、採用されたコンテキストとスコアを表示
            print("\n[Context Used]")
            for i, (sc, _chunk, src) in enumerate(hits, 1):
                print(f"  [{i}] {os.path.basename(src)}  score={sc:.3f}")
            print()
    except KeyboardInterrupt:
        print("\n終了します。")
