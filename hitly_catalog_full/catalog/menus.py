from telebot import types


def hitly_catalog_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🤖 AI-консультанты", callback_data="cat_ai"),
        types.InlineKeyboardButton("📞 Автоматизация продаж", callback_data="cat_sales"),
        types.InlineKeyboardButton("💬 Обработка сообщений", callback_data="cat_messages"),
        types.InlineKeyboardButton("🌐 Сайт и онлайн-чат", callback_data="cat_website"),
        types.InlineKeyboardButton("📲 Telegram и WhatsApp", callback_data="cat_messengers"),
        types.InlineKeyboardButton("📊 CRM и аналитика", callback_data="cat_crm"),
        types.InlineKeyboardButton("☎️ Голосовой AI", callback_data="cat_voice"),
        types.InlineKeyboardButton("📈 Маркетинг", callback_data="cat_marketing"),
        types.InlineKeyboardButton("⚙️ Автоматизация процессов", callback_data="cat_automation"),
        types.InlineKeyboardButton("🎓 Обучение и внедрение", callback_data="cat_training"),
        types.InlineKeyboardButton("🏗 Решения по отраслям", callback_data="cat_industries"),
        types.InlineKeyboardButton("❓ FAQ по Hitly", callback_data="cat_faq"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="menu"),
    )
    return kb
