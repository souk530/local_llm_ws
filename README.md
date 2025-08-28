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

## 🚀 セットアップ手順

### 1️⃣ Ollamaのインストール

[公式サイトからダウンロード](https://ollama.com/download)

**Windows の場合:**
1. `ollama-windows.exe` をダウンロード
2. ダブルクリックで実行
3. インストール完了まで待つ

**Mac の場合:**
```bash
brew install ollama
```

または [公式サイト](https://ollama.com/download) からダウンロード

![インストール画面](./demo-image/image.png)

### gitのインストール
https://git-scm.com/downloads/win

#### powershellで確認
git --version


### 2️⃣ LLMモデルのダウンロード

コマンドプロンプト/ターミナルで実行：

```bash
# モデルをダウンロード（約2.2GB、時間がかかります）
ollama pull phi3

# モデルが正常に動作するかテスト
ollama run phi3
```

![モデル実行画面](./demo-image/ollama.png)

### 3️⃣ Python環境のセットアップ

```bash
# 仮想環境の作成
python -m venv .venv

#　管理者権限のpowershellで下だけ実行
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser


# 仮想環境の有効化
# Windows の場合:
.venv\Scripts\activate

# Mac/Linux の場合:
source .venv/bin/activate

# 成功すると先頭に (.venv) が表示される
# 例: (.venv) PS C:\Users\username\local_llm_ws>

# 必要なライブラリをインストール
pip install requests
```

### 4️⃣ サンプルプログラムの実行

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



---
了解です！😊
PowerShellで **`git clone`** を実行するためには、以下の準備が必要です。
「初めてPowerShellでGitを使う」前提で、インストールから設定、SSH鍵まで詳しく解説します。

---

## **全体の流れ**

1. **Gitのインストール**
2. **PowerShellでGitコマンドが使えるか確認**
3. **ユーザー情報の設定（必須）**
4. **SSHキーまたはHTTPS認証の準備**
5. **`git clone` の実行**
6. **トラブルシューティング**

---

## **1. Gitのインストール**

### **方法①：wingetでインストール（推奨）**

Windows 10以降ならPowerShellから一発でインストールできます。

```powershell
winget install --id Git.Git -e --source winget
```

### **方法②：公式サイトからインストール**

* [https://git-scm.com/download/win](https://git-scm.com/download/win)
* インストーラーを実行 → 「Git BashをPATHに追加」にチェック ✅

---

## **2. PowerShellでGitコマンドが使えるか確認**

PowerShellを開いて以下を実行：

```powershell
git --version
```

* 例：`git version 2.46.0`
  → 表示されればOK
* 「`git` が認識されません」と出た場合 → PATH設定が必要なので、再インストール時に **“Add Git to PATH”** を有効にする

---

## **3. ユーザー情報の設定（必須）**

初めてGitを使う場合、ユーザー名とメールアドレスを設定します。

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

設定を確認するには：

```powershell
git config --list
```

---

## **4. 認証方法の準備**

### **① HTTPSでcloneする場合（簡単）**

GitHubやGitLabのリポジトリURLをHTTPSで指定すれば、最初の一回だけユーザー名とパスワードを入力すればOK。

例：

```powershell
git clone https://github.com/username/repo.git
```

ただし2021年以降、GitHubは**パスワード認証が廃止**されたため、**Personal Access Token (PAT)** を使う必要があります。

PATの発行方法：

* GitHub → **Settings** → **Developer settings** → **Personal access tokens**
* 「repo」スコープを付与 → 発行されたトークンをHTTPSパスワードとして使う

---

### **② SSHでcloneする場合（おすすめ）**

#### **SSHキーを作成**

```powershell
ssh-keygen -t rsa -b 4096 -C "you@example.com"
```

Enterを3回押せば `C:\Users\<ユーザー名>\.ssh\id_rsa` に鍵が作られます。

#### **公開鍵をGitHubに登録**

```powershell
cat ~/.ssh/id_rsa.pub
```

* 出てきたキーをコピー
* GitHub → **Settings** → **SSH and GPG keys** → **New SSH key** → 貼り付け

#### **SSH接続をテスト**

```powershell
ssh -T git@github.com
```

「Hi username! You’ve successfully authenticated」と出ればOK。

#### **SSHでclone**

```powershell
git clone git@github.com:username/repo.git
```

---

## **5. git clone の実行**

プロジェクトを保存したいディレクトリに移動して実行：

```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/username/repo.git
```

またはSSH版：

```powershell
git clone git@github.com:username/repo.git
```

cloneが終わったら移動：

```powershell
cd repo
```

---

## **6. トラブルシューティング**

| エラー                             | 原因         | 対策                                               |
| ------------------------------- | ---------- | ------------------------------------------------ |
| `git: command not found`        | Git未インストール | wingetまたは公式サイトからインストール                           |
| `Permission denied (publickey)` | SSHキー未設定   | SSHキーを生成＆GitHubに登録                               |
| `Authentication failed`         | HTTPSで認証失敗 | PATを使う or SSH接続に切り替え                             |
| `SSL certificate problem`       | 企業ネットワークなど | `git config --global http.sslVerify false`（自己責任） |

---

## **まとめ**

| 作業          | コマンド例                                            |
| ----------- | ------------------------------------------------ |
| Gitインストール   | `winget install --id Git.Git -e --source winget` |
| バージョン確認     | `git --version`                                  |
| ユーザー設定      | `git config --global user.name "Your Name"`      |
| HTTPS clone | `git clone https://github.com/username/repo.git` |
| SSH鍵生成      | `ssh-keygen -t rsa -b 4096 -C "you@example.com"` |
| SSH clone   | `git clone git@github.com:username/repo.git`     |

---

もし希望があれば、**PowerShell専用の自動セットアップスクリプト**を書いて、
「Gitインストール → SSH鍵生成 → GitHub登録URLを開く → clone実行」まで自動化できます。

これ、やりますか？

