 ## https://ollama.com/download
 980MBくらいあるから事前インストール推奨

# ollamaにモデルのダウンロード
 ollama pull deepseek-coder:8b

# モデルの実行
 ollama run deepseek-coder:8b


# ローカルLLM体験ワークショップ：Ollama & DeepSeek編

![構成図](./demo-image/ollama.png)

---

## 1. Ollamaセットアップ 時間がかかるから事前に実行しておくことを推奨します！

[公式手順に沿ってインストール](https://ollama.com/download)
![インストール時の画面](./demo-image/ollama.png)

- Windows: `ollama-windows.exe` をダブルクリック
- Mac: `brew install ollama` でもOK

![これを実行](./demo-image/image.png)

## 2. モデルダウンロード

```bash
ollama pull phi3
ollama run phi3


仮想環境の作成
python -m venv .venv

仮想環境の有効化
.venv\Scripts\activate
→ (.venv) PS C:\Users\~~~~~~~\local_llm_ws>

必要なライブラリをインストール
 pip install requests


