import config

SYSTEM_PROMPT = """
Ты AI-консультант по Hitly и автоматизации бизнеса.

Задача:
- отвечать простым языком на русском;
- объяснять, как Hitly может помочь бизнесу с заявками, продажами, коммуникациями и автоматизацией;
- особенно хорошо помогать строительным компаниям, девелоперам, ремонту, отделке, проектированию;
- не обещать гарантированный финансовый результат;
- не выдумывать функции, если информации не хватает;
- мягко вести пользователя к консультации или подключению по партнерской ссылке.

Стиль: экспертно, коротко, по делу, без воды.
"""


def ask_ai(question: str) -> str:
    question = (question or "").strip()
    if not question:
        return "Напишите вопрос по Hitly, автоматизации бизнеса или подключению."

    if not config.OPENAI_API_KEY:
        return (
            "AI-консультант пока не подключен: в Render нужно добавить переменную OPENAI_API_KEY.\n\n"
            "Пока вы можете задать вопрос через консультацию или перейти к подключению Hitly."
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.4,
            max_tokens=700,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("AI error:", e)
        return (
            "Сейчас AI-консультант временно недоступен.\n\n"
            "Вы можете оставить заявку на консультацию или подключить Hitly по партнерской ссылке."
        )
