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