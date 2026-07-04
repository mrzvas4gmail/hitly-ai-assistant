import config
import telebot
from telebot import types
from fastapi import FastAPI, Request

from ai import ask_ai
from database import init_db, save_user, save_lead, get_stats

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML")
app = FastAPI()
user_state = {}


def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🤖 AI-консультант", callback_data="ai"),
        types.InlineKeyboardButton("🏗️ Возможности Hitly", callback_data="features"),
        types.InlineKeyboardButton("💼 Подойдет ли моему бизнесу", callback_data="fit"),
        types.InlineKeyboardButton("🚀 Как подключиться", callback_data="connect"),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
    )
    return kb


def action_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🚀 Подключить Hitly", url=config.PARTNER_LINK),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
        types.InlineKeyboardButton("🤖 Задать еще вопрос", callback_data="ai"),
        types.InlineKeyboardButton("🏠 Главное меню", callback_data="menu"),
    )
    return kb


def notify_admin(text):
    admin_id = str(config.ADMIN_CHAT_ID).strip()
    if admin_id:
        try:
            bot.send_message(int(admin_id), text)
        except Exception as e:
            print("Admin notify error:", e)


@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user)
    user_state.pop(message.chat.id, None)

    text = (
        "👋 <b>Здравствуйте!</b>\n\n"
        "Я AI-консультант по Hitly и автоматизации бизнеса.\n\n"
        "Помогу понять:\n"
        "• как Hitly может помочь вашему бизнесу;\n"
        "• какие процессы можно автоматизировать;\n"
        "• подойдет ли решение вашей компании;\n"
        "• как подключиться и с чего начать.\n\n"
        "Выберите раздел:"
    )

    bot.send_message(message.chat.id, text, reply_markup=main_menu())


@bot.message_handler(commands=["myid"])
def myid(message):
    bot.send_message(message.chat.id, f"Ваш ADMIN_CHAT_ID:\n<code>{message.chat.id}</code>")


@bot.message_handler(commands=["stats"])
def stats(message):
    if str(message.chat.id) != str(config.ADMIN_CHAT_ID).strip():
        bot.send_message(message.chat.id, "Команда доступна только администратору.")
        return

    users, leads = get_stats()
    bot.send_message(
        message.chat.id,
        f"📈 <b>Статистика</b>\n\n"
        f"Пользователей: {users}\n"
        f"Лидов: {leads}"
    )


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    save_user(call.from_user)
    chat_id = call.message.chat.id

    if call.data == "menu":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "🏠 Главное меню", reply_markup=main_menu())

    elif call.data == "ai":
        user_state[chat_id] = {"mode": "ai"}
        bot.send_message(
            chat_id,
            "🤖 <b>AI-консультант Hitly</b>\n\n"
            "Задайте вопрос про Hitly, автоматизацию, заявки, продажи, CRM или подключение.\n\n"
            "Например:\n"
            "• Как Hitly поможет строительной компании?\n"
            "• Какие процессы можно автоматизировать?\n"
            "• Как подключиться?\n"
            "• Подойдет ли Hitly моему бизнесу?"
        )

    elif call.data == "features":
        text = (
            "🏗️ <b>Возможности Hitly</b>\n\n"
            "Hitly может помочь бизнесу автоматизировать коммуникации, обработку заявок "
            "и работу с клиентами.\n\n"
            "<b>Что можно улучшить:</b>\n"
            "• скорость ответа клиентам;\n"
            "• обработку заявок из разных каналов;\n"
            "• первичные консультации;\n"
            "• повторные касания;\n"
            "• контроль работы отдела продаж;\n"
            "• передачу клиента менеджеру.\n\n"
            "Особенно полезно для строительных компаний, ремонта, девелоперов, услуг и бизнеса с потоком заявок."
        )
        bot.send_message(chat_id, text, reply_markup=action_menu())

    elif call.data == "fit":
        text = (
            "💼 <b>Подойдет ли Hitly вашему бизнесу?</b>\n\n"
            "Hitly может быть полезен, если у вас:\n\n"
            "• есть входящие заявки;\n"
            "• клиенты пишут в мессенджеры;\n"
            "• менеджеры не всегда отвечают быстро;\n"
            "• часть обращений теряется;\n"
            "• много повторяющихся вопросов;\n"
            "• нужен порядок в коммуникациях.\n\n"
            "Чтобы понять точнее, задайте AI-консультанту вопрос о вашей компании."
        )
        bot.send_message(chat_id, text, reply_markup=action_menu())

    elif call.data == "connect":
        text = (
            "🚀 <b>Как подключиться к Hitly</b>\n\n"
            "1. Перейдите по партнерской ссылке.\n"
            "2. Зарегистрируйтесь в Hitly.\n"
            "3. Изучите возможности платформы.\n"
            "4. Начните с одного процесса: например, первичный ответ клиентам.\n"
            "5. При необходимости оставьте заявку на консультацию.\n\n"
            "Лучше начинать не со сложного внедрения, а с конкретной задачи бизнеса."
        )
        bot.send_message(chat_id, text, reply_markup=action_menu())

    elif call.data == "lead":
        user_state[chat_id] = {"mode": "lead", "step": "name"}
        bot.send_message(chat_id, "📞 <b>Заявка на консультацию</b>\n\nКак вас зовут?")

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
        handle_ai(message)

    elif state.get("mode") == "lead":
        handle_lead(message, state)


def handle_ai(message):
    chat_id = message.chat.id
    question = message.text.strip()

    if len(question) < 3:
        bot.send_message(chat_id, "Напишите вопрос подробнее.")
        return

    bot.send_chat_action(chat_id, "typing")

    answer = ask_ai(question)

    bot.send_message(chat_id, answer, reply_markup=action_menu())
    user_state.pop(chat_id, None)


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

        save_lead(
            chat_id,
            state["name"],
            state["company"],
            state["phone"],
            state["telegram"]
        )

        lead_text = (
            "🔥 <b>Новый лид из Telegram-бота</b>\n\n"
            f"Имя: {state['name']}\n"
            f"Компания: {state['company']}\n"
            f"Телефон: {state['phone']}\n"
            f"Telegram: {state['telegram']}\n"
            f"User ID: {chat_id}"
        )

        notify_admin(lead_text)
        user_state.pop(chat_id, None)

        bot.send_message(
            chat_id,
            "Спасибо! Заявка принята ✅\n\n"
            "Также вы можете сразу подключить Hitly по партнерской ссылке ниже.",
            reply_markup=action_menu()
        )


@app.on_event("startup")
def on_startup():
    init_db()

    webhook_url = config.WEBHOOK_URL.rstrip("/") + f"/webhook/{config.BOT_TOKEN}"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    print("Бот запущен ✅")
    print("Webhook set:", webhook_url)


@app.get("/")
def home():
    return {"status": "ok", "message": "Hitly AI Assistant is running"}


@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != config.BOT_TOKEN:
        return {"ok": False}

    data = await request.json()
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])

    return {"ok": True}
    
