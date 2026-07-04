import telebot
from telebot import types
from fastapi import FastAPI, Request, HTTPException

import config
from ai import ask_ai
from database import init_db, save_user, save_lead, get_stats

if not config.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is empty. Add BOT_TOKEN in Render Environment.")

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML")
app = FastAPI()
user_state = {}


def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🤖 Спросить AI-консультанта", callback_data="ask_ai"),
        types.InlineKeyboardButton("🏗️ Возможности Hitly для бизнеса", callback_data="features"),
        types.InlineKeyboardButton("💼 Подойдет ли моему бизнесу", callback_data="fit"),
        types.InlineKeyboardButton("🚀 Как подключиться", callback_data="connect"),
        types.InlineKeyboardButton("📞 Бесплатная консультация", callback_data="lead"),
    )
    return kb


def after_answer_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🚀 Подключить Hitly", url=config.PARTNER_LINK),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
        types.InlineKeyboardButton("🤖 Задать еще вопрос", callback_data="ask_ai"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="menu"),
    )
    return kb


def notify_admin(text):
    if config.ADMIN_CHAT_ID:
        try:
            bot.send_message(int(config.ADMIN_CHAT_ID), text)
        except Exception as e:
            print("Admin notify error:", e)


@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user)
    user_state.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "👋 <b>Здравствуйте!</b>\n\n"
        "Я AI-консультант по Hitly и автоматизации бизнеса.\n\n"
        "Помогу понять:\n"
        "• какие процессы можно автоматизировать;\n"
        "• как Hitly может помочь с заявками и продажами;\n"
        "• подойдет ли решение вашему бизнесу;\n"
        "• как подключиться и с чего начать.\n\n"
        "Выберите действие:",
        reply_markup=main_menu(),
    )


@bot.message_handler(commands=["myid"])
def myid(message):
    bot.send_message(message.chat.id, f"Ваш ADMIN_CHAT_ID:\n<code>{message.chat.id}</code>")


@bot.message_handler(commands=["stats"])
def stats(message):
    if str(message.chat.id) != str(config.ADMIN_CHAT_ID):
        bot.send_message(message.chat.id, "Команда доступна только администратору.")
        return
    users, leads = get_stats()
    bot.send_message(message.chat.id, f"📈 <b>Статистика</b>\n\nПользователей: {users}\nЛидов: {leads}")


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    save_user(call.from_user)
    chat_id = call.message.chat.id

    if call.data == "menu":
        user_state.pop(chat_id, None)
        bot.edit_message_text("🏠 <b>Главное меню</b>", chat_id, call.message.message_id, reply_markup=main_menu())

    elif call.data == "ask_ai":
        user_state[chat_id] = {"mode": "ai"}
        bot.send_message(
            chat_id,
            "🤖 <b>AI-консультант Hitly</b>\n\n"
            "Напишите вопрос про Hitly, автоматизацию заявок, отдел продаж, CRM или подключение.\n\n"
            "Например: <i>Как Hitly поможет строительной компании?</i>"
        )

    elif call.data == "features":
        bot.edit_message_text(
            "🏗️ <b>Возможности Hitly для бизнеса</b>\n\n"
            "Hitly можно использовать для автоматизации коммуникаций, обработки заявок "
            "и контроля клиентского пути.\n\n"
            "Что это может дать:\n"
            "• быстрый первый ответ клиенту;\n"
            "• снижение риска потерять заявку;\n"
            "• автоматизация типовых вопросов;\n"
            "• помощь менеджерам;\n"
            "• понятный следующий шаг для клиента.",
            chat_id,
            call.message.message_id,
            reply_markup=after_answer_menu(),
        )

    elif call.data == "fit":
        bot.edit_message_text(
            "💼 <b>Кому может подойти Hitly?</b>\n\n"
            "Hitly особенно полезен бизнесу, где есть входящие заявки, менеджеры, переписки "
            "и необходимость быстро отвечать клиентам.\n\n"
            "Подходит для строительных компаний, девелоперов, ремонта, отделки, проектирования, "
            "производства стройматериалов и других компаний с отделом продаж.",
            chat_id,
            call.message.message_id,
            reply_markup=after_answer_menu(),
        )

    elif call.data == "connect":
        bot.edit_message_text(
            "🚀 <b>Как подключиться к Hitly</b>\n\n"
            "1. Перейдите по партнерской ссылке.\n"
            "2. Зарегистрируйтесь.\n"
            "3. Начните с одного процесса: первый ответ клиенту, заявки или типовые вопросы.\n"
            "4. Если нужна помощь — оставьте заявку на консультацию.",
            chat_id,
            call.message.message_id,
            reply_markup=after_answer_menu(),
        )

    elif call.data == "lead":
        user_state[chat_id] = {"mode": "lead", "step": "name"}
        bot.send_message(chat_id, "📞 <b>Бесплатная консультация</b>\n\nКак вас зовут?")

    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    save_user(message.from_user)
    chat_id = message.chat.id
    state = user_state.get(chat_id)

    if not state:
        bot.send_message(chat_id, "Выберите действие в меню 👇", reply_markup=main_menu())
        return

    if state.get("mode") == "ai":
        question = message.text.strip()
        if len(question) < 3:
            bot.send_message(chat_id, "Напишите вопрос чуть подробнее.")
            return
        bot.send_chat_action(chat_id, "typing")
        answer = ask_ai(question)
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, answer, reply_markup=after_answer_menu())
        return

    if state.get("mode") == "lead":
        handle_lead(message, state)


def handle_lead(message, state):
    chat_id = message.chat.id
    text = message.text.strip()

    if state["step"] == "name":
        state["name"] = text
        state["step"] = "company"
        bot.send_message(chat_id, "Название вашей компании?")
        return

    if state["step"] == "company":
        state["company"] = text
        state["step"] = "phone"
        bot.send_message(chat_id, "Ваш телефон для связи?")
        return

    if state["step"] == "phone":
        state["phone"] = text
        state["telegram"] = f"@{message.from_user.username}" if message.from_user.username else "не указан"
        save_lead(chat_id, state["name"], state["company"], state["phone"], state["telegram"])
        notify_admin(
            "🔥 <b>Новый лид из Telegram-бота</b>\n\n"
            f"Имя: {state['name']}\n"
            f"Компания: {state['company']}\n"
            f"Телефон: {state['phone']}\n"
            f"Telegram: {state['telegram']}\n"
            f"User ID: {chat_id}"
        )
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "Спасибо! Заявка принята ✅", reply_markup=after_answer_menu())


@app.on_event("startup")
def on_startup():
    init_db()
    if not config.WEBHOOK_URL:
        print("WEBHOOK_URL is empty. Add WEBHOOK_URL in Render Environment.")
        return
    webhook = f"{config.WEBHOOK_URL}/webhook/{config.BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook)
    print("Webhook set:", webhook.replace(config.BOT_TOKEN, "***"))


@app.get("/")
def root():
    return {"status": "ok", "service": "Hitly AI Telegram Bot"}


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    if token != config.BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    json_data = await request.json()
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return {"ok": True}
