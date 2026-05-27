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

# Старые копии .env с шаблоном 9:00 → 11:00 (остальные значения не трогаем)
$envPath = Join-Path $Root ".env"
$envLines = Get-Content -LiteralPath $envPath
$migrated = $false
$newEnv = foreach ($line in $envLines) {
    if ($line -match '^\s*REMINDER_HOUR\s*=\s*9\s*$') {
        $migrated = $true
        "REMINDER_HOUR=11"
    } else {
        $line
    }
}
if ($migrated) {
    $newEnv | Set-Content -LiteralPath $envPath -Encoding utf8
    Write-Host "В .env обновлено: REMINDER_HOUR=11 (раньше было 9)."
}

pip install -r requirements.txt -q
python main.py
