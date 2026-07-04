# Hitly AI Telegram Bot — Clean Webhook Version

Это чистая версия Telegram-бота без long polling. Она работает через webhook, поэтому не должна давать ошибку 409 Conflict.

## Файлы для GitHub
Загрузите в репозиторий все файлы:
- bot.py
- ai.py
- config.py
- database.py
- requirements.txt
- README.md
- .gitignore

## Render
Создайте Web Service, не Background Worker.

Build Command:
```bash
pip install -r requirements.txt
```

Start Command:
```bash
uvicorn bot:app --host 0.0.0.0 --port $PORT
```

Environment Variables:
- BOT_TOKEN = токен Telegram от BotFather
- OPENAI_API_KEY = ключ OpenAI
- PARTNER_LINK = https://hitly.ru/register?ref=KHbU5Q8Y
- YOUR_TELEGRAM = https://t.me/mrzvas4
- ADMIN_CHAT_ID = можно оставить пустым, потом написать боту /myid
- WEBHOOK_URL = публичный URL вашего Render Web Service, например https://dmp-ai-sales-bot1.onrender.com

После первого запуска откройте Telegram и напишите боту /start.
