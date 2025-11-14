import os
import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("8286119515:AAF7uT66t_8UEzbAMKyfFvXhXEcGxSmtScc")

async def clear_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Удаляем предыдущее сообщение БОТА
    if context.user_data.get("last_bot_message"):
        try:
            await context.user_data["last_bot_message"].delete()
        except:
            pass

    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except:
            pass
    else:
        try:
            await update.message.delete()
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await clear_prev(update, context)

    keyboard = [
        [InlineKeyboardButton("Вытянуть карту дня", callback_data="card")],
        [InlineKeyboardButton("Послушать медитацию", callback_data="med")],
        [InlineKeyboardButton("Получить уникальную практику", callback_data="practice")],
    ]

    photo_path = "assets/hello.jpg"

    sent = await update.effective_chat.send_photo(
        photo=open(photo_path, "rb"),
        caption=(
            "Рада, что ты с нами! \n\n"
            "Давай познакомимся еще раз. Меня зовут Карина — психолог, автор Т-игр, МАК и дневников практик.\n\n"
            "Выбери, что ты хочешь узнать сегодня:"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data["last_bot_message"] = sent

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await clear_prev(update, context)

    if query.data == "card":

        cards_path = "assets/cards"
        card = random.choice(os.listdir(cards_path))
        card_file = f"{cards_path}/{card}"

        sent = await query.message.chat.send_photo(
            photo=open(card_file, "rb"),
            caption="Это твоя Карта Дня. Что она может значить для тебя?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Записаться на консультацию", url="https://t.me/karinamokk")],
                [InlineKeyboardButton("МАК карты на Wildberries", url="https://www.wildberries.ru/seller/4096634/")],
                [InlineKeyboardButton("Вернуться в меню", callback_data="menu")]
            ])
        )
        context.user_data["last_bot_message"] = sent

    elif query.data == "med":

        sent = await query.message.chat.send_message(
            "Выбери медитацию:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Исполнение желаний", url="https://vkvideo.ru/video-113948441_456239058")],
                [InlineKeyboardButton("Уверенность себе", url="https://vkvideo.ru/video-113948441_456239057")],
                [InlineKeyboardButton("Прощение себя", url="https://vkvideo.ru/video-113948441_456239052")],
                [InlineKeyboardButton("Назад", callback_data="menu")]
            ])
        )
        context.user_data["last_bot_message"] = sent

    elif query.data == "practice":

        sent = await query.message.chat.send_message(
            "Стоимость уникальной практики — 1000 рублей.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Получить практику — 1000 ₽", url="https://vkvideo.ru/@km.psygame")],
                [InlineKeyboardButton("Назад", callback_data="menu")]
            ])
        )
        context.user_data["last_bot_message"] = sent

    elif query.data == "menu":
        await start(update, context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
