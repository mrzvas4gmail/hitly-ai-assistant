import config
from telebot import types


def catalog_action_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🚀 Подключить Hitly", url=config.PARTNER_LINK),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
        types.InlineKeyboardButton("🤖 Задать вопрос AI", callback_data="ai"),
        types.InlineKeyboardButton("⬅️ Каталог возможностей", callback_data="hitly_catalog"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="menu"),
    )
    return kb
