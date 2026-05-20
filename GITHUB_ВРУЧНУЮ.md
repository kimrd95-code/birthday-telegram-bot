# Залить на GitHub без скрипта

Скопируйте команды **целиком**, вставляйте в PowerShell. Кавычки должны быть прямые `"`, не «ёлочки».

## 1. Перейти в папку

```powershell
Set-Location "C:\Users\Lenovo\Desktop\ИИ. Обучение\Cursor\telegram-birthday-bot"
```

## 2. Войти в GitHub (один раз)

```powershell
gh auth login -h github.com -p https -w
```

В браузере подтвердите вход.

## 3. Создать репозиторий и отправить код

```powershell
gh repo create birthday-telegram-bot --public --source=. --remote=origin --push
```

Готово. Ссылка будет в выводе команды.
