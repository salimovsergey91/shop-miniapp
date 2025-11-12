import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8286119515:AAF7uT66t_8UEzbAMKyfFvXhXEcGxSmtScc"

# ====== ЭТАП 1 — СТАРТ ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Добро пожаловать в бот канала «С Жизнью на Ты». \n\n"
        "Здесь ты познакомишься с практиками и медитациями, а также сможешь получить "
        "эксклюзивный контент по подписке, которого нет в открытом доступе.\n\n"
        "Прежде чем мы начнем, нужно твое согласие.\n\n"
        "Нажимая на кнопку «Принимаю», вы подтверждаете ознакомление и принятие "
        "условий Оферты и даете согласие на обработку персональных данных в соответствии "
        "с Политикой конфиденциальности, а также даете согласие на рассылку специальных предложений."
    )

    keyboard = [
        [InlineKeyboardButton("Принимаю", callback_data="accept")],
        [InlineKeyboardButton("Не принимаю", callback_data="decline")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ====== ЭТАП 2 — ОБРАБОТКА СОГЛАСИЯ ======
async def handle_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "accept":
        text = (
            "Рада, что ты с нами! \n\n"
            "Давай познакомимся еще раз. Меня зовут Карина, я психолог, автор Т-игр, МАК и дневников практик.\n\n"
            "Выбери, что ты хочешь узнать сегодня:"
        )
        keyboard = [
            [InlineKeyboardButton("Вытянуть карту дня", callback_data="card_day")],
            [InlineKeyboardButton("Послушать медитацию", callback_data="meditations")],
            [InlineKeyboardButton("Получить уникальную практику", callback_data="unique_practice")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "decline":
        await query.edit_message_text(
            "Жаль, что ты не с нами. Ты всегда можешь вернуться и начать снова с команды /start."
        )

# ====== ЭТАП 3 — КАРТА ДНЯ ======
async def card_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "Это твоя  *Карта Дня*.\n"
        "Подумай, что это может означать для тебя?\n\n"
        "Хочешь, мы можем разобрать это вместе:"
    )

    keyboard = [
        [InlineKeyboardButton("Записаться на консультацию", callback_data="consultation")],
        [InlineKeyboardButton("МАК карты на Wildberries", url="https://www.wildberries.ru")],
        [InlineKeyboardButton("Вернуться в основное меню", callback_data="main_menu")]
    ]

    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== ЭТАП 4 — КОНСУЛЬТАЦИЯ ======
async def consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "Личная консультация длительностью 30 минут.\n"
        "Мы разберем твой запрос и найдем решение.\n\n"
        "Стоимость: *5000 рублей*."
    )

    keyboard = [
        [InlineKeyboardButton(" Оплатить консультацию — 5000₽", url="https://yoomoney.ru")]
    ]

    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== ЭТАП 5 — МЕДИТАЦИИ ======
async def meditations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "Выбери медитацию, которая тебе нужна сегодня"

    keyboard = [
        [InlineKeyboardButton("На расслабление", callback_data="med_relax")],
        [InlineKeyboardButton("На мотивацию", callback_data="med_motivation")],
        [InlineKeyboardButton("Исполнение желания", callback_data="med_desire")],
        [InlineKeyboardButton("Вернуться в основное меню", callback_data="main_menu")]
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ====== ЭТАП 6 — УНИКАЛЬНАЯ ПРАКТИКА ======
async def unique_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "Выбери практику из закрытого доступа \n"
        "Стоимость: *1000 рублей*."
    )

    keyboard = [
        [InlineKeyboardButton(" Получить уникальную практику — 1000₽", url="https://yoomoney.ru")],
        [InlineKeyboardButton(" Вернуться в основное меню", callback_data="main_menu")]
    ]

    await query.edit_message_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== ЭТАП 7 — ВОЗВРАТ В ОСНОВНОЕ МЕНЮ ======
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "Рада, что ты с нами снова \n\n"
        "Меня зовут Карина, я психолог, автор Т-игр, МАК и дневников практик.\n\n"
        "Выбери, что ты хочешь узнать сегодня:"
    )
    keyboard = [
        [InlineKeyboardButton(" Вытянуть карту дня", callback_data="card_day")],
        [InlineKeyboardButton(" Послушать медитацию", callback_data="meditations")],
        [InlineKeyboardButton(" Получить уникальную практику", callback_data="unique_practice")]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ====== СОЕДИНЯЕМ ВСЕ ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_agreement, pattern="^(accept|decline)$"))
    app.add_handler(CallbackQueryHandler(card_day, pattern="^card_day$"))
    app.add_handler(CallbackQueryHandler(consultation, pattern="^consultation$"))
    app.add_handler(CallbackQueryHandler(meditations, pattern="^meditations$"))
    app.add_handler(CallbackQueryHandler(unique_practice, pattern="^unique_practice$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()