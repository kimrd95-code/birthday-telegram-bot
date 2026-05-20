# Запуск бота (PowerShell)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Создан файл .env — откройте его и вставьте BOT_TOKEN от @BotFather"
    exit 1
}

pip install -r requirements.txt -q
python main.py
