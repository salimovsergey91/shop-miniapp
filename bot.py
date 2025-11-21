import os
import asyncio
from aiohttp import web
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

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")


# ---------- УДАЛЕНИЕ ПРЕДЫДУЩИХ СООБЩЕНИЙ ----------
async def clear_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Удаляем последнее сообщение бота
    last = context.user_data.get("last_bot_message")
    if last:
        try:
            await last.delete()
        except:
            pass

    # Удаляем сообщение-команду или callback-сообщение
    try:
        if update.callback_query:
            await update.callback_query.message.delete()
        elif update.message:
            await update.message.delete()
    except:
        pass


# ---------- /START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_prev(update, context)

    keyboard = [
        [InlineKeyboardButton("Послушать медитацию", callback_data="med")],
        [InlineKeyboardButton("Получить уникальную практику", callback_data="practice")],
        [InlineKeyboardButton("Записаться на консультацию", url="https://t.me/karinamokk")]
    ]

    photo_path = "assets/welcome.jpg"

    with open(photo_path, 'rb') as f:
        sent = await update.effective_chat.send_photo(
            photo=f,
            caption=(
                "Рада, что ты с нами! \n\n"
                "Меня зовут Карина — психолог, автор Т-игр, МАК и дневников практик.\n\n"
                "Выбери, что ты хочешь сегодня:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    context.user_data["last_bot_message"] = sent


# ---------- ОБРАБОТКА КНОПОК ----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await clear_prev(update, context)

    if query.data == "med":
        sent = await query.message.chat.send_message(
            "Выбери медитацию:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Исполнение желаний", url="https://vkvideo.ru/video-113948441_456239058")],
                [InlineKeyboardButton("Уверенность в себе", url="https://vkvideo.ru/video-113948441_456239057")],
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
        await start(update.callback_query, context)


# ---------- WEBHOOK-HANDLER ----------
async def handle(request):
    data = await request.json()

    application = request.app["application"]
    bot = application.bot

    update = Update.de_json(data, bot)

    await application.process_update(update)
    return web.Response(text="ok")


# ---------- MAIN ----------
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    # Проверка наличия URL
    if not WEBHOOK_URL:
        raise RuntimeError("ENV RENDER_EXTERNAL_URL не задан!")

    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

    server = web.Application()
    server["application"] = app
    server.router.add_post("/webhook", handle)

    await app.initialize()
    await app.start()

    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Бот запущен. Webhook = {WEBHOOK_URL}/webhook")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
