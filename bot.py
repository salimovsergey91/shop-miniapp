# bot.py
import os
import random
import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 8080))
ASSETS_BASE_URL = os.getenv("ASSETS_BASE_URL")  # optional: public URL to folder with images (e.g. Supabase Storage)

if not BOT_TOKEN:
    logger.error("BOT_TOKEN не задан в переменных окружения")
    raise SystemExit("BOT_TOKEN required")

# ---------- ВСПОМОГАТЕЛЬНЫЕ ----------
async def clear_prev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("last_bot_message"):
        try:
            await context.user_data["last_bot_message"].delete()
        except Exception:
            pass

    if update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass
    else:
        try:
            await update.message.delete()
        except Exception:
            pass

# ---------- КОМАНДЫ ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_prev(update, context)

    keyboard = [
        [InlineKeyboardButton("Вытянуть карту дня", callback_data="card")],
        [InlineKeyboardButton("Послушать медитацию", callback_data="med")],
        [InlineKeyboardButton("Получить уникальную практику", callback_data="practice")],
    ]

    # Если задан ASSETS_BASE_URL, то используем URL-изображение (удобно для Supabase Storage).
    if ASSETS_BASE_URL:
        photo_url = f"{ASSETS_BASE_URL.rstrip('/')}/welcome.JPG"
        sent = await update.effective_chat.send_photo(
            photo=photo_url,
            caption=(
                "Рада, что ты с нами! \n\n"
                "Давай познакомимся еще раз. Меня зовут Карина — психолог, автор Т-игр, МАК и дневников практик.\n\n"
                "Выбери, что ты хочешь узнать сегодня:"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        photo_path = "assets/welcome.JPG"
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
        # cards: if ASSETS_BASE_URL => fetch random card by filename list from LOCAL or from env list
        cards_path = "assets/cards"
        if ASSETS_BASE_URL:
            # expect environment variable CARDS_LIST with filenames separated by comma
            cards_list_env = os.getenv("CARDS_LIST")
            if not cards_list_env:
                await query.message.chat.send_message("Не найдены карты: установите CARDS_LIST или положите карты в assets/cards")
                return
            cards = [c.strip() for c in cards_list_env.split(",") if c.strip()]
            card = random.choice(cards)
            card_url = f"{ASSETS_BASE_URL.rstrip('/')}/cards/{card}"
            sent = await query.message.chat.send_photo(
                photo=card_url,
                caption="Это твоя Карта Дня. Что она может значить для тебя?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Записаться на консультацию", url="https://t.me/karinamokk")],
                    [InlineKeyboardButton("МАК карты на Wildberries", url="https://www.wildberries.ru/seller/4096634/")],
                    [InlineKeyboardButton("Вернуться в меню", callback_data="menu")]
                ])
            )
        else:
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

# ---------- WEBHOOK ----------
async def handle(request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="invalid json")

    update = Update.de_json(data, request.app["bot"])
    await request.app["application"].process_update(update)
    return web.Response(status=200)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    # set webhook (Telegram)
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL / RENDER_EXTERNAL_URL not set in env")
        raise SystemExit("WEBHOOK URL required")
    webhook_full = f"{WEBHOOK_URL.rstrip('/')}/webhook"
    await app.bot.set_webhook(webhook_full)
    logger.info("Webhook set to %s", webhook_full)

    # aiohttp server to receive Telegram updates
    server = web.Application()
    server["bot"] = app.bot
    server["application"] = app
    server.router.add_post("/webhook", handle)

    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("HTTP server running on port %s", PORT)

    # Initialize and start the Application (without polling)
    await app.initialize()
    await app.start()
    logger.info("Telegram application started")

    # keep running until cancelled
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        logger.info("Shutting down")
        await app.stop()
        await app.shutdown()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
