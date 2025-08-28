import os
import glob
import time
import math
import pickle
import hashlib
from typing import List, Dict, Tuple

import google.generativeai as genai

# =========================================
# 設定
# =========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("環境変数 GEMINI_API_KEY を設定してください。")

genai.configure(api_key=GEMINI_API_KEY)

GEN_MODEL_DEFAULT = "gemini-1.5-flash"   # "gemini-1.5-pro" でもOK
EMBED_MODEL = "text-embedding-004"

DATA_DIR = "./data"
INDEX_PATH = "./rag_index.pkl"
CHUNK_CHARS = 800
CHUNK_OVERLAP = 200
TOP_K = 4

# =========================================
# 生成（あなたのベース関数のGemini版）
# =========================================
def chat_gemini(prompt: str, model: str = GEN_MODEL_DEFAULT) -> str:
    gm = genai.GenerativeModel(model)
    resp = gm.generate_content(prompt)
    # エラー時は例外が投げられる想定
    return (resp.text or "").strip()

# =========================================
# 埋め込み
# =========================================
def embed_texts(texts: List[str]) -> List[List[float]]:
    out = []
    for t in texts:
        # 1件ずつ呼ぶ（安定・簡単）。大量ならバッチ化も可
        r = genai.embed_content(model=EMBED_MODEL, content=t)
        out.append(r["embedding"])
    return out

# =========================================
# データ読み込み & チャンク
# =========================================
def read_txt_files(data_dir: str) -> List[Tuple[str, str]]:
    files = sorted(glob.glob(os.path.join(data_dir, "*.txt")))
    out = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                out.append((fp, f.read()))
        except UnicodeDecodeError:
            with open(fp, "r", encoding="cp932", errors="ignore") as f:
                out.append((fp, f.read()))
    return out

def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks, n, start = [], len(text), 0
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n: break
        start = max(0, end - overlap)
    return chunks

# =========================================
# インデックス作成/ロード
# =========================================
def hash_corpus(files: List[Tuple[str, str]]) -> str:
    h = hashlib.sha256()
    for path, text in files:
        h.update(path.encode("utf-8"))
        h.update(str(os.path.getmtime(path)).encode("utf-8"))
        h.update(str(len(text)).encode("utf-8"))
    return h.hexdigest()

def build_or_load_index(data_dir: str = DATA_DIR, index_path: str = INDEX_PATH) -> Dict:
    files = read_txt_files(data_dir)
    if not files:
        raise RuntimeError(f"{data_dir} に .txt が見つかりません。")

    corpus_sig = hash_corpus(files)

    if os.path.exists(index_path):
        try:
            with open(index_path, "rb") as f:
                idx = pickle.load(f)
            if idx.get("corpus_sig") == corpus_sig and idx.get("embed_model") == EMBED_MODEL:
                return idx
        except Exception:
            pass

    chunks, metas = [], []
    for path, text in files:
        for c in chunk_text(text, CHUNK_CHARS, CHUNK_OVERLAP):
            if c.strip():
                chunks.append(c)
                metas.append({"source": path})

    print(f"[RAG] チャンク数: {len(chunks)} / 埋め込み計算中…")
    embeddings = embed_texts(chunks)

    idx = {
        "corpus_sig": corpus_sig,
        "embed_model": EMBED_MODEL,
        "chunks": chunks,
        "metas": metas,
        "embeddings": embeddings,
        "built_at": time.time(),
    }
    with open(index_path, "wb") as f:
        pickle.dump(idx, f)
    print(f"[RAG] インデックス作成完了 → {index_path}")
    return idx

# =========================================
# 検索 & 類似度
# =========================================
def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0.0 or nb == 0.0: return 0.0
    return dot / (na * nb)

def retrieve(index: Dict, query: str, top_k: int = TOP_K) -> List[Tuple[float, str, str]]:
    qv = embed_texts([query])[0]
    scores = []
    for vec, chunk, meta in zip(index["embeddings"], index["chunks"], index["metas"]):
        s = cosine(qv, vec)
        scores.append((s, chunk, meta["source"]))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]

# =========================================
# プロンプト生成 & 実行
# =========================================
def build_prompt_with_context(user_query: str, contexts: List[Tuple[float, str, str]]) -> str:
    ctx_blocks = []
    for i, (_sc, chunk, src) in enumerate(contexts, 1):
        ctx_blocks.append(f"[{i}] Source: {os.path.basename(src)}\n{chunk.strip()}")
    ctx_text = "\n\n---\n\n".join(ctx_blocks)

    return f"""あなたは検索強化されたアシスタントです。以下のコンテキストの内容に基づいて日本語で答えてください。コンテキストに無い場合は「不明です」と述べてください。引用は [1], [2] のように付けてください。

# コンテキスト
{ctx_text}

# 質問
{user_query}

# 回答（日本語・必要に応じて [1], [2] で出典を明示）
"""

def rag_answer(user_query: str, gen_model: str = GEN_MODEL_DEFAULT):
    index = build_or_load_index(DATA_DIR, INDEX_PATH)
    hits = retrieve(index, user_query, TOP_K)
    prompt = build_prompt_with_context(user_query, hits)
    answer = chat_gemini(prompt, model=gen_model)
    return answer, hits

# =========================================
# CLI
# =========================================
if __name__ == "__main__":
    try:
        while True:
            q = input("ユーザー: ").strip()
            if not q: continue
            if q.lower() in {"exit", "quit"}: break
            ans, hits = rag_answer(q, gen_model=GEN_MODEL_DEFAULT)
            print("\nAI:", ans)
            print("\n[Context Used]")
            for i, (sc, _c, src) in enumerate(hits, 1):
                print(f"  [{i}] {os.path.basename(src)}  score={sc:.3f}")
            print()
    except KeyboardInterrupt:
        print("\n終了します。")
