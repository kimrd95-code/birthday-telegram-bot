# Запуск бота бесплатно на Render (24/7)

Бот будет работать **без включённого компьютера**. На бесплатном тарифе Render используется **Background Worker** — процесс с `python main.py` крутится на сервере.

---

## Важно про бесплатный тариф

| Что | Как на Render Free |
|-----|---------------------|
| Работа бота | Да, пока сервис **Running** |
| Лимит часов | ~750 часов/мес на все бесплатные сервисы аккаунта |
| База SQLite | При **пересборке/редиплое** данные могут **сброситься** — коллегам нужно снова `/start`. Не жмите Redeploy без нужды |
| `.env` на сервере | **Не загружают** — переменные задаются в панели Render |

---

## Часть 1. Выложить код на GitHub

Render подключается к **GitHub**. Нужен репозиторий **только с папкой бота** (или весь проект, но тогда укажете подпапку).

### Вариант А — через сайт GitHub (проще)

1. Зайдите на [github.com](https://github.com), войдите в аккаунт.
2. **New repository** → имя, например `birthday-telegram-bot` → **Create** (без README).
3. На странице репозитория: **uploading an existing file**.
4. Перетащите **все файлы** из папки  
   `telegram-birthday-bot`  
   (кроме `.venv`, `data/`, `.env` — их не заливайте).
5. **Commit changes**.

### Вариант Б — через Git в PowerShell

```powershell
cd "c:\Users\Lenovo\Desktop\ИИ. Обучение\Cursor\telegram-birthday-bot"
git init
git add .
git commit -m "Birthday Telegram bot"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/birthday-telegram-bot.git
git push -u origin main
```

*(Создайте пустой репозиторий на GitHub заранее.)*

---

## Часть 2. Создать сервис на Render

1. Зайдите на [render.com](https://render.com) → **Get Started** → войдите через **GitHub**.
2. **New +** → **Background Worker** (не Web Service).
3. **Connect repository** → выберите `birthday-telegram-bot`.
4. Настройки:

   | Поле | Значение |
   |------|----------|
   | **Name** | `birthday-telegram-bot` |
   | **Region** | Frankfurt (или ближайший) |
   | **Branch** | `main` |
   | **Root Directory** | оставьте пустым, если в репозитории только файлы бота; если репозиторий — вся папка Cursor, укажите `telegram-birthday-bot` |
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `python main.py` |
   | **Instance Type** | **Free** |

5. Прокрутите до **Environment Variables** → **Add Environment Variable**:

   | Key | Value |
   |-----|--------|
   | `BOT_TOKEN` | токен от @BotFather |
   | `ADMIN_TELEGRAM_IDS` | ваш Id от @userinfobot |
   | `TIMEZONE` | `Europe/Moscow` |
   | `REMINDER_HOUR` | `9` |

6. **Create Background Worker**.

7. Дождитесь статуса **Live** / **Running** (первая сборка 3–10 минут).

8. Вкладка **Logs** — должно быть что-то вроде:  
   `Scheduler: daily at 9:00 ... Bot starting...`

---

## Часть 3. Проверка

1. В Telegram откройте бота → **Start** → регистрация.
2. Отправьте `/test_reminders` (если ваш ID в `ADMIN_TELEGRAM_IDS`).
3. На Render в **Logs** не должно быть ошибок `BOT_TOKEN` или `Forbidden`.

---

## Часть 4. Обновление бота после правок

1. Загрузите изменения на GitHub (commit + push или Upload file).
2. Render обычно **деплоит сам** (Auto-Deploy).
3. После деплоя база на бесплатном диске может обнулиться — предупредите коллег при больших обновлениях.

**Локальный ПК:** `python main.py` на компьютере **остановите**, иначе два процесса с одним токеном будут конфликтовать (двойные ответы, ошибки).

---

## Blueprint (одной кнопкой)

Если репозиторий уже на GitHub с файлом `render.yaml` в корне:

1. Render Dashboard → **New +** → **Blueprint**.
2. Укажите репозиторий → Render создаст Worker по `render.yaml`.
3. Вручную добавьте секреты `BOT_TOKEN` и `ADMIN_TELEGRAM_IDS` (помечены `sync: false`).

---

## Частые ошибки

**Build failed** — проверьте `requirements.txt`, Root Directory, Python 3.12 в `runtime.txt`.

**Deploy failed / сразу падает** — нет `BOT_TOKEN` в Environment Variables.

**Бот не отвечает** — на Render сервис не Running; или бот ещё запущен у вас на ПК с тем же токеном.

**Напоминания не в 09:00** — часовой пояс `TIMEZONE=Europe/Moscow`, сервер Render в UTC, но APScheduler использует вашу зону из конфига.

**Превышен лимит 750 ч/мес** — бесплатный лимит исчерпан до следующего месяца; временно запуск на ПК или платный план.

---

## Стоимость

- **Free Worker** — $0, с лимитами выше.
- Карта для Free часто не нужна, но Render может попросить при регистрации — смотрите актуальные правила на сайте.

После деплоя компьютер можно **выключать** — бот живёт на Render.
