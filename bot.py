import config
import telebot
from site_audit import analyze_site
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
        types.InlineKeyboardButton("🔎 Пройти AI-аудит бизнеса", callback_data="audit_start"),
        types.InlineKeyboardButton("🏗️ Возможности Hitly", callback_data="features"),
        types.InlineKeyboardButton("💼 Подойдет ли моему бизнесу", callback_data="fit"),
        types.InlineKeyboardButton("🚀 Как подключиться", callback_data="connect"),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
        types.InlineKeyboardButton("🌐 Анализ сайта", callback_data="site_audit"),
    )
    return kb


def action_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🔎 Пройти AI-аудит", callback_data="audit_start"),
        types.InlineKeyboardButton("🚀 Подключить Hitly", url=config.PARTNER_LINK),
        types.InlineKeyboardButton("📞 Получить консультацию", callback_data="lead"),
        types.InlineKeyboardButton("🤖 Задать вопрос AI", callback_data="ai"),
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
        "• какие процессы можно автоматизировать;\n"
        "• где бизнес может терять заявки;\n"
        "• подойдет ли Hitly вашей компании;\n"
        "• с чего начать внедрение.\n\n"
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
        
        elif call.data == "site_audit":
    user_state[chat_id] = {"mode": "site_audit"}
    bot.send_message(
        chat_id,
        "🌐 <b>AI-анализ сайта</b>\n\n"
        "Отправьте ссылку на сайт.\n\n"
        "Например:\n"
        "https://example.ru"
    )

    elif call.data == "ai":
        user_state[chat_id] = {"mode": "ai"}
        bot.send_message(
            chat_id,
            "🤖 <b>AI-консультант Hitly</b>\n\n"
            "Задайте вопрос про Hitly, автоматизацию, заявки, CRM, продажи или подключение.\n\n"
            "Например:\n"
            "• Как Hitly поможет строительной компании?\n"
            "• Какие процессы можно автоматизировать?\n"
            "• Подойдет ли Hitly моему бизнесу?"
        )

    elif call.data == "audit_start":
        user_state[chat_id] = {"mode": "audit", "step": "business_type"}
        bot.send_message(
            chat_id,
            "🔎 <b>AI-аудит бизнеса</b>\n\n"
            "Ответьте на 7 вопросов, и я покажу, где можно усилить продажи и автоматизацию.\n\n"
            "1/7 Чем занимается ваша компания?\n\n"
            "Например: строительство, ремонт, недвижимость, производство, услуги."
        )

    elif call.data == "features":
        text = (
            "🏗️ <b>Возможности Hitly</b>\n\n"
            "Hitly может помочь автоматизировать коммуникации, обработку заявок "
            "и работу с клиентами.\n\n"
            "<b>Что можно улучшить:</b>\n"
            "• скорость ответа клиентам;\n"
            "• обработку заявок из разных каналов;\n"
            "• первичные консультации;\n"
            "• повторные касания;\n"
            "• контроль отдела продаж;\n"
            "• передачу клиента менеджеру."
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
            "Лучше всего начать с AI-аудита бизнеса."
        )
        bot.send_message(chat_id, text, reply_markup=action_menu())

    elif call.data == "connect":
        text = (
            "🚀 <b>Как подключиться к Hitly</b>\n\n"
            "1. Перейдите по партнерской ссылке.\n"
            "2. Зарегистрируйтесь в Hitly.\n"
            "3. Изучите возможности платформы.\n"
            "4. Начните с одного процесса: например, первичный ответ клиентам.\n"
            "5. При необходимости оставьте заявку на консультацию."
        )
        bot.send_message(chat_id, text, reply_markup=action_menu())

    elif call.data == "lead":
        user_state[chat_id] = {"mode": "lead", "step": "name"}
        bot.send_message(chat_id, "📞 <b>Заявка на консультацию</b>\n\nКак вас зовут?")

    bot.answer_callback_query(call.id)

def handle_site_audit(message):
    chat_id = message.chat.id
    site_url = message.text.strip()

    if not site_url.startswith("http"):
        bot.send_message(
            chat_id,
            "Пожалуйста, отправьте ссылку в формате:\nhttps://example.ru"
        )
        return

    bot.send_chat_action(chat_id, "typing")

    result = analyze_site(site_url)

    user_state.pop(chat_id, None)

    bot.send_message(
        chat_id,
        result,
        reply_markup=action_menu()
    )

@bot.message_handler(content_types=["text"])
def text_handler(message):
    save_user(message.from_user)
    chat_id = message.chat.id
    state = user_state.get(chat_id)

elif state.get("mode") == "site_audit":
    handle_site_audit(message)

    if not state:
        bot.send_message(chat_id, "Выберите действие в меню 👇", reply_markup=main_menu())
        return

    if state.get("mode") == "ai":
        handle_ai(message)

    elif state.get("mode") == "audit":
        handle_audit(message, state)

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


def handle_audit(message, state):
    chat_id = message.chat.id
    answer = message.text.strip()

    if state["step"] == "business_type":
        state["business_type"] = answer
        state["step"] = "leads"
        bot.send_message(
            chat_id,
            "2/7 Сколько заявок в месяц вы примерно получаете?\n\n"
            "Например: до 30, 30–100, 100–500, больше 500."
        )
        return

    if state["step"] == "leads":
        state["leads"] = answer
        state["step"] = "channels"
        bot.send_message(
            chat_id,
            "3/7 Откуда приходят заявки?\n\n"
            "Например: сайт, Авито, Telegram, WhatsApp, реклама, сарафанное радио."
        )
        return

    if state["step"] == "channels":
        state["channels"] = answer
        state["step"] = "crm"
        bot.send_message(
            chat_id,
            "4/7 Есть ли у вас CRM или система учета заявок?\n\n"
            "Например: нет, Битрикс24, amoCRM, таблицы, другая система."
        )
        return

    if state["step"] == "crm":
        state["crm"] = answer
        state["step"] = "loss_problem"
        bot.send_message(
            chat_id,
            "5/7 Где чаще всего теряются клиенты?\n\n"
            "Например: долго отвечаем, забываем перезвонить, нет повторных касаний, менеджеры работают по-разному."
        )
        return

    if state["step"] == "loss_problem":
        state["loss_problem"] = answer
        state["step"] = "response_time"
        bot.send_message(
            chat_id,
            "6/7 Как быстро вы обычно отвечаете клиенту?\n\n"
            "Например: сразу, до 15 минут, через час, на следующий день."
        )
        return

    if state["step"] == "response_time":
        state["response_time"] = answer
        state["step"] = "goal"
        bot.send_message(
            chat_id,
            "7/7 Что хотите улучшить в первую очередь?\n\n"
            "Например: быстрее отвечать, автоматизировать продажи, контролировать менеджеров, не терять заявки."
        )
        return

    if state["step"] == "goal":
        state["goal"] = answer
        report = generate_audit_report(state)

        notify_admin(
            "🔎 <b>Пользователь прошел AI-аудит</b>\n\n"
            f"Бизнес: {state.get('business_type')}\n"
            f"Заявки: {state.get('leads')}\n"
            f"Каналы: {state.get('channels')}\n"
            f"CRM: {state.get('crm')}\n"
            f"Проблема: {state.get('loss_problem')}\n"
            f"Скорость ответа: {state.get('response_time')}\n"
            f"Цель: {state.get('goal')}\n"
            f"User ID: {chat_id}"
        )

        user_state.pop(chat_id, None)
        bot.send_message(chat_id, report, reply_markup=action_menu())


def generate_audit_report(state):
    business = state.get("business_type", "")
    leads = state.get("leads", "")
    channels = state.get("channels", "")
    crm = state.get("crm", "")
    loss_problem = state.get("loss_problem", "")
    response_time = state.get("response_time", "")
    goal = state.get("goal", "")

    risk_score = 0
    text = f"{crm} {loss_problem} {response_time} {channels}".lower()

    if "нет" in text or "таблиц" in text:
        risk_score += 2
    if "долго" in text or "час" in text or "следующ" in text:
        risk_score += 2
    if "забы" in text or "теря" in text:
        risk_score += 2
    if "авито" in text or "telegram" in text or "whatsapp" in text or "реклама" in text:
        risk_score += 1

    if risk_score <= 2:
        risk_level = "средний"
        automation_level = "средний"
        priority = "6/10"
    elif risk_score <= 5:
        risk_level = "повышенный"
        automation_level = "ниже среднего"
        priority = "8/10"
    else:
        risk_level = "высокий"
        automation_level = "низкий"
        priority = "9/10"

    return (
        "📊 <b>Результаты AI-аудита бизнеса</b>\n\n"
        f"<b>Компания:</b> {business}\n"
        f"<b>Заявки в месяц:</b> {leads}\n"
        f"<b>Каналы заявок:</b> {channels}\n"
        f"<b>CRM:</b> {crm}\n"
        f"<b>Главная проблема:</b> {loss_problem}\n"
        f"<b>Скорость ответа:</b> {response_time}\n"
        f"<b>Цель:</b> {goal}\n\n"
        f"⚠️ <b>Риск потери клиентов:</b> {risk_level}\n"
        f"⚙️ <b>Уровень автоматизации:</b> {automation_level}\n"
        f"🚀 <b>Приоритет внедрения:</b> {priority}\n\n"
        "<b>Что стоит автоматизировать в первую очередь:</b>\n"
        "• первичный ответ клиентам 24/7;\n"
        "• сбор заявок из разных каналов;\n"
        "• передачу обращения менеджеру;\n"
        "• повторные касания;\n"
        "• контроль заявок и коммуникаций.\n\n"
        "<b>Рекомендация:</b>\n"
        "Начать с простого сценария: автоматизация первого ответа клиенту и фиксация каждой заявки.\n\n"
        "Можете оставить заявку на консультацию или подключить Hitly по партнерской ссылке."
    )


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
    
