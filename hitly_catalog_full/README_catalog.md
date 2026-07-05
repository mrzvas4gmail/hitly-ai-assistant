# Hitly Catalog Module

Готовый модуль каталога возможностей Hitly для Telegram-бота.

## Как подключить в bot.py

1. В импорты добавьте:

```python
from catalog.callback import handle_catalog_callback
from catalog.menus import hitly_catalog_menu
```

2. В main_menu замените кнопку возможностей на:

```python
types.InlineKeyboardButton("🚀 Каталог возможностей Hitly", callback_data="hitly_catalog"),
```

3. В callbacks(call) сразу после определения chat_id добавьте:

```python
if handle_catalog_callback(bot, call):
    bot.answer_callback_query(call.id)
    return
```

4. Commit changes → Render → Manual Deploy → Clear build cache & deploy.
