# Publish bot to GitHub
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Install: winget install GitHub.cli"
    exit 1
}

gh auth status 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Login to GitHub in browser..."
    gh auth login -h github.com -p https -w
}

$repoName = "birthday-telegram-bot"
Write-Host "Creating repo $repoName ..."

gh repo create $repoName --public --source=. --remote=origin --push --description "Telegram birthday bot"

if ($LASTEXITCODE -eq 0) {
    gh repo view --json url -q .url
    Write-Host "Done. Next: Render - Background Worker - connect this repo."
} else {
    Write-Host "If repo exists, run: git push -u origin main"
}
