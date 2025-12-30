import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
FOUNDER_URL = "https://t.me/karinamokk"

CARDS_DIR = "assets/cards"

QUESTIONS = [
    ("Как ты сейчас чувствуешь себя эмоционально?",
     ["Спокойно", "Тревожно", "Устало", "Раздражённо"]),
    ("Что сейчас беспокоит больше всего?",
     ["Отношения", "Деньги", "Самооценка", "Будущее"]),
    ("Как ты спишь в последнее время?",
     ["Хорошо", "Плохо", "Бессонница", "Поверхностно"]),
    ("Есть ли ощущение, что ты застрял(а)?",
     ["Да", "Иногда", "Нет"]),
    ("Чего хочется больше всего?",
     ["Спокойствия", "Уверенности", "Поддержки", "Ясности"]),
]


# ---------- МЕНЮ ----------
def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎧 Послушать практику", callback_data="meditations")],
        [InlineKeyboardButton("🧠 Пройти диагностику состояния", callback_data="diagnostic")],
        [InlineKeyboardButton("🔮 Вытянуть карту дня", callback_data="card_day")],
        [InlineKeyboardButton("💬 Записаться на консультацию", url=FOUNDER_URL)],
    ])


# ---------- /START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    with open("assets/welcome.mp4", "rb") as video:
        await update.message.reply_video_note(video)

    await update.message.reply_text(
        "Рада тебе 💛\nВыбери, с чего хочешь начать:",
        reply_markup=menu_keyboard()
    )


# ---------- КНОПКИ ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "meditations":
        await query.message.reply_text(
            "Выбери практику:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Исполнение желаний", url="https://vkvideo.ru/video-113948441_456239058")],
                [InlineKeyboardButton("💪 Уверенность в себе", url="https://vkvideo.ru/video-113948441_456239057")],
                [InlineKeyboardButton("🌿 Прощение себя", url="https://vkvideo.ru/video-113948441_456239052")],
            ])
        )

    elif data == "diagnostic":
        context.user_data["step"] = 0
        await send_question(query, context)

    elif data.startswith("ans_"):
        context.user_data["step"] += 1
        if context.user_data["step"] < len(QUESTIONS):
            await send_question(query, context)
        else:
            await diagnostic_result(query)

    elif data == "card_day":
        cards = os.listdir(CARDS_DIR)
        card = random.choice(cards)
        with open(os.path.join(CARDS_DIR, card), "rb") as img:
            await query.message.reply_photo(
                img,
                caption="Это твоя карта дня.\nПодумай, что она может означать для тебя ✨"
            )


# ---------- ВОПРОС ----------
async def send_question(query, context):
    step = context.user_data["step"]
    text, answers = QUESTIONS[step]

    keyboard = [
        [InlineKeyboardButton(a, callback_data=f"ans_{a}")]
        for a in answers
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------- РЕЗУЛЬТАТ ----------
async def diagnostic_result(query):
    with open("assets/diag_result.mp4", "rb") as video:
        await query.message.reply_video_note(video)

    await query.message.reply_text(
        "Спасибо за ответы 💛\n"
        "Если хочешь глубже разобрать своё состояние — записывайся на консультацию.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Записаться на консультацию", url=FOUNDER_URL)]
        ])
    )


# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()


if __name__ == "__main__":
    main()
