# Публикация бота на GitHub (один раз после входа в аккаунт)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host "Установите GitHub CLI: winget install GitHub.cli"
    exit 1
}

$status = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Сейчас откроется вход в GitHub (браузер или код в терминале)."
    Write-Host "Выберите: GitHub.com -> HTTPS -> Login with a web browser"
    gh auth login -h github.com -p https -w
}

$repoName = "birthday-telegram-bot"
Write-Host "Создаю репозиторий $repoName и отправляю код..."

gh repo create $repoName --public --source=. --remote=origin --push --description "Telegram bot: birthday reminders and congrats chat"

if ($LASTEXITCODE -eq 0) {
    $url = gh repo view --json url -q .url
    Write-Host ""
    Write-Host "Готово! Репозиторий: $url"
    Write-Host "Дальше: Render -> New Background Worker -> подключите этот репозиторий (см. RENDER_DEPLOY.md)"
} else {
    Write-Host "Если репозиторий уже есть, выполните:"
    Write-Host "  git remote add origin https://github.com/ВАШ_ЛОГИН/$repoName.git"
    Write-Host "  git push -u origin main"
}
