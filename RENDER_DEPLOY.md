# Render бесплатно (2025–2026): Web Service, не Worker

На Render **бесплатный план** есть только у **Web Service**.  
**Background Worker** — только платные Instance Type (от ~$7/мес).

Бот переведён на режим **Webhook**: бесплатный Web Service + бесплатный **cron-job.org** для напоминаний в 09:00.

---

## Что выбрать в Render

| Поле | Значение |
|------|----------|
| Тип сервиса | **Web Service** (не Background Worker) |
| Instance Type | **Free** (если есть в списке для Web) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py` |
| Health Check Path | `/` |

---

## Environment Variables (обязательно)

| Key | Value |
|-----|--------|
| `BOT_TOKEN` | токен @BotFather |
| `ADMIN_TELEGRAM_IDS` | ваш Telegram Id |
| `USE_WEBHOOK` | `true` |
| `CRON_SECRET` | длинная случайная строка, напр. `mySecretCron2026xyz` |
| `TIMEZONE` | `Europe/Moscow` |
| `REMINDER_HOUR` | `9` |

`RENDER_EXTERNAL_URL` Render подставит **сам** — не добавляйте вручную.

После деплоя в **Logs** должно быть: `Mode: webhook` и `Telegram webhook set`.

---

## Шаг: напоминания в 09:00 (cron-job.org)

Бесплатный Web на Render **засыпает** без трафика. Напоминания запускает внешний cron:

1. Зайдите на [cron-job.org](https://cron-job.org) (бесплатная регистрация).
2. **Create cron job**:
   - **Title:** Birthday bot reminders
   - **URL:**  
     `https://ВАШ-СЕРВИС.onrender.com/cron/daily?key=ВАШ_CRON_SECRET`  
     (скопируйте URL сервиса из Render Dashboard + тот же `CRON_SECRET`, что в Variables)
   - **Schedule:** каждый день **09:00**, timezone **Europe/Moscow**
   - **Request method:** GET
3. Сохраните.

Проверка: откройте URL в браузере — должно показать `ok` (не `forbidden`).

---

## Опционально: не давать боту засыпать

На Free Web сервис «просыпается» от сообщений в Telegram (webhook).  
Для надёжности можно добавить второй cron на cron-job.org:

- URL: `https://ВАШ-СЕРВИС.onrender.com/`
- Каждые **14 минут**

Тогда первый ответ иногда будет с задержкой 30–60 сек после сна — это норма Free tier.

---

## Локально на ПК (как раньше)

В `.env` **не** ставьте `USE_WEBHOOK` — бот работает в режиме **polling** + встроенный планировщик 09:00.

---

## Платный Worker на Render

Если нужен Worker без webhook и cron-job.org — выберите минимальный **Instance Type** (платный) и в Variables **уберите** `USE_WEBHOOK` (или `false`), Start Command `python main.py` — снова polling + APScheduler.

---

## Частые ошибки

| Симптом | Решение |
|---------|---------|
| Только платные Instance Type | Вы создали **Worker** → удалите, создайте **Web Service** |
| `forbidden` на cron URL | Неверный `key=` в URL, должен совпадать с `CRON_SECRET` |
| Бот не отвечает после сна | Подождите ~1 мин или добавьте ping каждые 14 мин |
| Два бота с одним токеном | Остановите `python main.py` на ПК |

---

## Обновление кода на GitHub

```powershell
cd "путь\к\telegram-birthday-bot"
git add .
git commit -m "Webhook mode for Render free"
git push
```

Render пересоберёт сервис сам.
