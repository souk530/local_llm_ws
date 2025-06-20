# ローカル推論ミニ実験ワークショップ

> **目的**: CPU‑only 環境でも動く超軽量 LLM を自力でビルドし、Python スクリプトからプロンプトを投げてみる。一連の流れを体験することで、クラウド API との違いや量子化の概念を理解する。

---

## 0. 事前条件

|        | 推奨                                     | 備考                |
| ------ | -------------------------------------- | ----------------- |
| OS     | Windows 10/11, macOS 11+, Ubuntu 22.04 | *WSL2 可*          |
| CPU    | SSE4.2 (Intel / AMD) or Apple Silicon  | GPU 不要            |
| Python | 3.9 – 3.12                             | `venv` or `conda` |
| Git    | 2.x                                    |                   |

> ⚠ **メモリ目安**: Tiny モデル (1.1 B) の 4‑bit 量子化で ≒ 0.8 GB‑RAM。

---

## 1. リポジトリ構成

```text
local-llm-demo/
├── .gitignore
├── README.md   ← このファイル
├── setup.sh    ← llama.cpp ビルド＋モデルDL (bash)
├── local_chat.py ← Python ラッパ (llama‑cpp‑python)
└── models/
    └── tinyllama-1.1b-chat.gguf (自動DL)
```

---

## 2. クイックスタート (TL;DR)

```bash
# 1️⃣ クローン
$ git clone https://github.com/<yourname>/local-llm-demo.git
$ cd local-llm-demo

# 2️⃣ 一発セットアップ (10〜15 分)
$ bash setup.sh

# 3️⃣ チャット開始
$ python local_chat.py "日本の首都は？"
```

---

## 3. 詳細ステップ

### 3.1 仮想環境作成

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
```

### 3.2 llama.cpp のビルド

`setup.sh` 内部で以下を実行しています。

```bash
# llama.cpp ソース取得
if [ ! -d "llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp.git
fi
cd llama.cpp
make -j$(nproc) LLAMA_NO_AVX2=1  # Apple Silicon は LLAMA_METAL=1
cd ..
```

### 3.3 量子化済み TinyLlama モデルの取得

```bash
MODEL_URL="https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.4-GGUF/resolve/main/TinyLlama-1.1B-Chat-v0.4.Q4_K_M.gguf"
mkdir -p models && wget -O models/tinyllama-1.1b-chat.gguf "$MODEL_URL"
```

> 🔍 *なぜ量子化?* — 重みを 16/8 bit ⇒ 4 bit へ圧縮し、メモリ帯域とサイズを削減。

### 3.4 Python 依存のインストール

```bash
pip install llama-cpp-python==0.2.* "python-dotenv<1" rich typer
```

---

## 4. スクリプト解説

### 4.1 `local_chat.py`

```python
#!/usr/bin/env python
"""最小 LLAMA cpp ラッパ。
$ python local_chat.py "こんにちは" --n-predict 128
"""
import argparse, pathlib, os
from llama_cpp import Llama, LlamaCompletion

ROOT = pathlib.Path(__file__).resolve().parent
MODEL = ROOT / "models" / "tinyllama-1.1b-chat.gguf"

parser = argparse.ArgumentParser()
parser.add_argument("prompt", help="ユーザプロンプト")
parser.add_argument("--n-predict", type=int, default=64, help="生成トークン数")
args = parser.parse_args()

llm = Llama(model_path=str(MODEL), n_ctx=2048, n_threads=os.cpu_count())
completion: LlamaCompletion = llm(
    args.prompt,
    max_tokens=args.n_predict,
    temperature=0.7,
    top_p=0.9,
    stop=["</s>", "USER:"],
)
print("\n=== 生成結果 ===\n", completion["choices"][0]["text"].strip())
```

> **ポイント**
>
> * `n_ctx`: 文脈長 (token) — 長いほどメモリ増
> * `n_threads`: 物理コア数 ≒ 最速

---

## 5. よくある質問 (FAQ)

| 質問                        | 回答                                                              |
| ------------------------- | --------------------------------------------------------------- |
| *M1/M2 Mac で Metal を使いたい* | `make LLAMA_METAL=1` でビルド & `local_chat.py` に `n_gpu_layers` 指定 |
| *AVX2 無し PC で失敗する*        | `make LLAMA_NO_AVX2=1` オプションを付与                                 |
| *モデルが大きすぎる*               | さらに 3‑bit (Q3\_K\_M) や distil 版を使う                              |
| *複数ターンチャットしたい*            | prompt を `system + history + user` フォーマットにしてループ実装               |

---

## 6. 教材応用アイデア

1. **パラメータ比較**: 温度 / Top‑p を変えて創造性を観察
2. **RAG 入門**: `chromadb` へ embedding を登録し、retrieval した文を prompt 前段に結合
3. **MAS 入門**: `crewai` で Retriever‑Agent ↔ Writer‑Agent を対話させる

---

## 7. ライセンス・引用

* コード: MIT
* TinyLlama‑1.1B‑Chat: Apache‑2.0（cc TinyLlama Team）

> 学術目的での利用を想定していますが、ライセンスに従ってください。

---

## 8. 参考リンク

* ggerganov/llama.cpp — [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)
* TinyLlama‑1.1B‑Chat GGUF — [https://huggingface.co/TinyLlama](https://huggingface.co/TinyLlama)
* llama‑cpp‑python — [https://github.com/abetlen/llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
