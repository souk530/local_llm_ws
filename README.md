# ローカルLLM体験ワークショップ：Ollama & DeepSeek編

![構成図](./demo-image/ollama.png)

---

## 📋 事前準備チェックリスト（重要！）

### ✅ 事前インストール必須項目
- [ ] **Ollama本体** (約980MB) - 必ず事前にインストール
- [ ] **LLMモデル** (約2.2GB) - 必ず事前にダウンロード  
- [ ] **Python 3.7以上**
- [ ] **requests ライブラリ**

---

## 🚀 環境構築手順

### 1️⃣ Googleアカウントの作成・ログイン
[Google](https://accounts.google.com/)でアカウントを作成またはログインしてください。

**確認方法:**
- Googleサービスにアクセスできることを確認

### 2️⃣ GitHubアカウントの作成
[GitHub](https://github.com/)でアカウントを作成してください。

**確認方法:**
```bash
# ブラウザでGitHubにログインできることを確認
```

### 3️⃣ Geminiへのアクセス確認
[Google AI Studio](https://aistudio.google.com/)にアクセスしてGeminiが利用可能か確認してください。

**確認方法:**
- Google AI StudioでAPIキーを取得可能か確認

### 4️⃣ WSL（Windows Subsystem for Linux）のインストール
**管理者権限のPowerShellで実行:**
```bash
wsl --install
```

**初期設定:**
1. Ubuntu初回起動時にユーザー名とパスワードを設定
2. パッケージを更新:
```bash
sudo apt update && sudo apt upgrade -y
```

**確認方法:**
```bash
wsl --version
```

### 5️⃣ Git設定（SSH接続でGitHubと連携）

#### Gitユーザー情報の設定
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

#### SSHキーの生成
```bash
ssh-keygen -t rsa -b 4096 -C "you@example.com"
```

#### 公開鍵をGitHubに登録
```bash
cat ~/.ssh/id_rsa.pub
```
出力された公開鍵をGitHub → Settings → SSH and GPG keys → New SSH keyに登録

**確認方法:**
```bash
ssh -T git@github.com
```

### 6️⃣ NVMのインストール
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
```

**確認方法:**
```bash
nvm --version
```

### 7️⃣ Node.jsのインストール
```bash
nvm install --lts
nvm use --lts
```

**確認方法:**
```bash
node -v
npm -v
```

### 8️⃣ Gemini CLIのインストール・認証
```bash
pip install google-generativeai
```

**環境変数の設定:**
```bash
export GEMINI_API_KEY="あなたのAPIキー"
```

**確認方法:**
```bash
python -c "import google.generativeai as genai; print('Gemini CLI ready')"
```

### 9️⃣ Ollamaのインストール
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**確認方法:**
```bash
ollama --version
```

### 🔟 Ollamaでモデルのインストール（phi3）
```bash
ollama pull phi3
ollama pull nomic-embed-text
```

**確認方法:**
```bash
ollama list
ollama run phi3 "Hello"
```

---

## 🏃 実行手順

### 1️⃣ Python環境のセットアップ

```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化
# Windows の場合:
.venv\Scripts\activate

# Mac/Linux の場合:
source .venv/bin/activate

# 成功すると先頭に (.venv) が表示される
# 例: (.venv) PS C:\Users\username\local_llm_ws>

# 必要なライブラリをインストール
pip install requests google-generativeai
```

### 2️⃣ サンプルプログラムの実行

```bash
# プログラムを実行
python test.py

# 質問を入力してEnter
# 例: "Pythonとは何ですか？"
```

---

## 📁 ファイル構成

```
local_llm_ws/
├── README.md           # このファイル
├── test.py            # サンプルプログラム
├── slide.html         # プレゼン資料
├── 目次.md             # 学習内容の目次
└── demo-image/        # 画像フォルダ
```

---

## 🛠️ トラブルシューティング

### よくある問題と解決方法

**Q: `ollama pull` でエラーが出る**
- A: インターネット接続を確認し、時間をおいて再実行

**Q: `python test.py` でエラーが出る**  
- A: 仮想環境が有効化されているか確認
- A: `pip install requests` が実行済みか確認

**Q: AI が応答しない**
- A: `ollama run phi3` でモデルが起動しているか確認
- A: `http://localhost:11434` にアクセスできるか確認

---

## 📚 学習コンテンツ

- **[プレゼン資料](./slide.html)** - ワークショップ用スライド
- **[学習目次](./目次.md)** - LLM/RAG/AIエージェントの概要

---

## 💡 ワークショップの流れ

1. **環境確認** - セットアップが完了しているか確認
2. **基礎理論** - LLM/RAG/AIエージェントの学習
3. **実践演習** - サンプルコードの実行と改良
4. **応用課題** - オリジナル機能の実装

準備完了したら講師にお声かけください！
