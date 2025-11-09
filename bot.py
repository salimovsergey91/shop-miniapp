from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8286119515:AAF7uT66t_8UEzbAMKyfFvXhXEcGxSmtScc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🛍 Открыть магазин",
            web_app=WebAppInfo(url="https://shop-miniapp.vercel.app/")
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать в наш магазин!\nНажми кнопку ниже, чтобы открыть каталог 👇",
        reply_markup=reply_markup
    )

def main():
    print("🤖 Бот запущен. Нажмите Ctrl+C для остановки.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
