# ============================================
# Node.js 一発セットアップ (Windows / PowerShell)
#  - nvm-windows のインストール
#  - Node.js (LTS) の導入＆切り替え
#  - npm 最新化 / yarn / pnpm 導入
#  管理者 PowerShell で実行してください
# ============================================

#----- 便利表示
function Write-Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }

#----- 管理者チェック
$IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
  ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
  Write-Err "管理者として PowerShell を実行してください。右クリック→『管理者として実行』"
  exit 1
}

#----- winget チェック
Write-Step "winget の確認"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  Write-Err "winget が見つかりません。Microsoft Store の『App Installer』を入れてから再実行してください。"
  exit 1
}
Write-OK "winget 利用可能"

#----- nvm-windows インストール
Write-Step "nvm-windows をインストール"
# 公式ID: CoreyButler.NVMforWindows
winget install --id CoreyButler.NVMforWindows -e --silent | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Warn "winget で nvm をインストールできなかった可能性があります（既に導入済みのことも）。続行します。"
} else {
  Write-OK "nvm-windows をインストールしました"
}

#----- nvm パスをこのセッションに通す（再起動なしで使えるように）
$nvmDir = "${env:ProgramFiles}\nvm"
$nodeDir = "${env:ProgramFiles}\nodejs"
if (Test-Path $nvmDir) {
  $env:Path = "$nvmDir;$nodeDir;$env:Path"
}
$nvmExe = Join-Path $nvmDir "nvm.exe"
if (-not (Test-Path $nvmExe)) {
  # nvm が PATH に入っている可能性もあるので再チェック
  $nvmExe = (Get-Command nvm -ErrorAction SilentlyContinue)?.Source
}
if (-not $nvmExe) {
  Write-Err "nvm.exe が見つかりません。PC を再起動して再実行するか、nvm を手動で確認してください。"
  exit 1
}
Write-OK "nvm パス設定 OK: $nvmExe"

#----- Node LTS をインストール（まずは 'lts' 指定 → ダメならフォールバック）
Write-Step "Node.js (LTS) のインストール"
$installed = $false
try {
  & $nvmExe install lts | Out-Null
  if ($LASTEXITCODE -eq 0) { $installed = $true }
} catch { }

if (-not $installed) {
  Write-Warn "'nvm install lts' が使えない環境のようです。LTSの既知バージョンでフォールバックします。"
  # フォールバック先（必要なら変更可）
  $fallbackVersion = "22.10.0"
  & $nvmExe install $fallbackVersion | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Err "Node.js のインストールに失敗しました。ネットワークやバージョンを確認してください。"
    exit 1
  }
  Write-OK "Node.js $fallbackVersion をインストールしました"
  & $nvmExe use $fallbackVersion | Out-Null
} else {
  Write-OK "Node.js (LTS) をインストールしました"
  # LTS を有効化
  try {
    & $nvmExe use lts | Out-Null
  } catch {
    Write-Warn "nvm use lts が失敗。最新インストール済みのバージョンに自動切替を試みます。"
    $list = (& $nvmExe list) -join "`n"
    $ver = ($list -split "`n" | Where-Object { $_ -match '^\s*v?\d+\.\d+\.\d+' } | Select-Object -Last 1).Trim()
    if (-not $ver) { Write-Err "利用可能な Node バージョンが見つかりません。"; exit 1 }
    & $nvmExe use $ver | Out-Null
  }
}

#----- node/npm の存在確認
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  # 念のため PATH を再注入
  $env:Path = "$nodeDir;$env:Path"
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Err "node コマンドが見つかりません。PowerShell を開き直すと認識される場合があります。"
  exit 1
}

#----- npm 最新化 & yarn / pnpm 導入
Write-Step "npm を最新化し、yarn / pnpm を導入"
npm install -g npm@latest
if ($LASTEXITCODE -ne 0) { Write-Warn "npm のアップデートに失敗しました（後で手動実行可）。" } else { Write-OK "npm を最新化しました" }

npm install -g yarn pnpm
if ($LASTEXITCODE -ne 0) { Write-Warn "yarn / pnpm の導入に失敗しました（後で手動実行可）。" } else { Write-OK "yarn / pnpm を導入しました" }

#----- バージョン表示
Write-Step "インストール結果"
Write-Host ("nvm  : " + (& $nvmExe version)) -ForegroundColor White
Write-Host ("node : " + (node -v)) -ForegroundColor White
Write-Host ("npm  : " + (npm -v)) -ForegroundColor White
Write-Host ("yarn : " + ((Get-Command yarn -ErrorAction SilentlyContinue) ? (yarn -v) : "未インストール")) -ForegroundColor White
Write-Host ("pnpm : " + ((Get-Command pnpm -ErrorAction SilentlyContinue) ? (pnpm -v) : "未インストール")) -ForegroundColor White

Write-OK "セットアップ完了！ 以後は例： 'nvm install 18.20.4' / 'nvm use 18.20.4' でバージョン切替できます。"
