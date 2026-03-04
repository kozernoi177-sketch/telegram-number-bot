from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8748444737:AAGYy9NYtWcU1U7eZjfEdKXONfA9R8KNkDI"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🔎 Найти номер"],
        ["⭐ Красивые номера", "💎 VIP номера"],
        ["📱 Операторы"],
        ["🎲 Случайный номер"],
        ["📞 Оформить номер"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в каталог красивых номеров 📱\n\nВыберите действие:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🔎 Найти номер":
        await update.message.reply_text(
            "Напишите цифры для поиска номера.\nНапример: 777"
        )

    elif text == "⭐ Красивые номера":
        await update.message.reply_text(
            "Раздел красивых номеров скоро появится."
        )

    elif text == "💎 VIP номера":
        await update.message.reply_text(
            "VIP номера скоро будут доступны."
        )

    elif text == "📱 Операторы":
        await update.message.reply_text(
            "Доступные операторы:\n\nМТС\nБилайн\nМегафон\nTele2\nСберМобайл"
        )

    elif text == "🎲 Случайный номер":
        await update.message.reply_text(
            "Пример красивого номера:\n+7 999 777 7777"
        )

    elif text == "📞 Оформить номер":
        await update.message.reply_text(
            "Напишите номер, который хотите оформить."
        )

    else:
        await update.message.reply_text(
            "Заявка принята. Мы свяжемся с вами."
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
