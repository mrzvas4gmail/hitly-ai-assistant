from catalog.menus import hitly_catalog_menu
from catalog.helpers import catalog_action_menu

from catalog.ai import TEXT as AI_TEXT
from catalog.sales import TEXT as SALES_TEXT
from catalog.messages import TEXT as MESSAGES_TEXT
from catalog.website import TEXT as WEBSITE_TEXT
from catalog.messengers import TEXT as MESSENGERS_TEXT
from catalog.crm import TEXT as CRM_TEXT
from catalog.voice import TEXT as VOICE_TEXT
from catalog.marketing import TEXT as MARKETING_TEXT
from catalog.automation import TEXT as AUTOMATION_TEXT
from catalog.training import TEXT as TRAINING_TEXT
from catalog.industries import TEXT as INDUSTRIES_TEXT
from catalog.faq import TEXT as FAQ_TEXT


CATALOG_PAGES = {
    "cat_ai": AI_TEXT,
    "cat_sales": SALES_TEXT,
    "cat_messages": MESSAGES_TEXT,
    "cat_website": WEBSITE_TEXT,
    "cat_messengers": MESSENGERS_TEXT,
    "cat_crm": CRM_TEXT,
    "cat_voice": VOICE_TEXT,
    "cat_marketing": MARKETING_TEXT,
    "cat_automation": AUTOMATION_TEXT,
    "cat_training": TRAINING_TEXT,
    "cat_industries": INDUSTRIES_TEXT,
    "cat_faq": FAQ_TEXT,
}


def handle_catalog_callback(bot, call):
    chat_id = call.message.chat.id

    if call.data == "hitly_catalog":
        bot.send_message(
            chat_id,
            "🚀 <b>Каталог возможностей Hitly</b>\n\nВыберите направление, которое хотите изучить:",
            reply_markup=hitly_catalog_menu()
        )
        return True

    if call.data in CATALOG_PAGES:
        bot.send_message(
            chat_id,
            CATALOG_PAGES[call.data],
            reply_markup=catalog_action_menu()
        )
        return True

    return False
