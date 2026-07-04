import config
from openai import OpenAI

SYSTEM_PROMPT = """
Ты AI-консультант по Hitly и автоматизации бизнеса.

Отвечай на русском языке, просто и по делу.
Помогай понять, как Hitly может помочь бизнесу:
- обработка заявок;
- автоматизация ответов;
- работа отдела продаж;
- CRM и коммуникации;
- подключение и первые шаги.

Не обещай гарантированный доход.
Если вопрос сложный — предложи консультацию.
В конце мягко предложи подключиться или задать уточняющий вопрос.
"""


def ask_ai(question: str) -> str:
    question = question.strip()

    if not question:
        return "Напишите ваш вопрос по Hitly или автоматизации бизнеса."

    if not config.OPENAI_API_KEY:
        return (
            "AI-консультант пока не подключен: в Render не найден OPENAI_API_KEY."
        )

    try:
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
        print("AI error:", repr(e))
        return (
            "AI-консультант временно недоступен.\n\n"
            "Возможная причина: OpenAI API-ключ, баланс или лимит проекта.\n"
            "Можно оставить заявку на консультацию или подключить Hitly по партнерской ссылке."
        )
