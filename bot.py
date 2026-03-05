import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes, ConversationHandler
)
import random

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 7006835550

# ========== РЕКВИЗИТЫ ==========
SBP_PHONE = "89820000177"
CARD_NUMBER = "2200 7017 0770 8514"
CARD_NAME = "Ахмад А."
CARD_BANK = "Т-Банк"

# ========== СОСТОЯНИЯ ==========
SEARCH, GET_NAME, GET_CITY, GET_SIMTYPE, GET_COMMENT, CONFIRM, PAYMENT_METHOD, WAIT_SCREENSHOT = range(8)

# ========== ТЕСТОВЫЕ НОМЕРА ==========
NUMBERS = [
    {"number": "+7 999 111 11 11", "price": 8000,  "operator": "МТС",     "category": "VIP"},
    {"number": "+7 999 777 77 77", "price": 15000, "operator": "Билайн",  "category": "VIP"},
    {"number": "+7 900 000 00 00", "price": 25000, "operator": "МегаФон", "category": "VIP"},
    {"number": "+7 977 333 33 33", "price": 5000,  "operator": "Tele2",   "category": "Красивый"},
    {"number": "+7 985 555 55 55", "price": 6000,  "operator": "МТС",     "category": "Красивый"},
    {"number": "+7 916 999 00 00", "price": 7000,  "operator": "Билайн",  "category": "Красивый"},
    {"number": "+7 926 123 45 67", "price": 2000,  "operator": "МегаФон", "category": "Обычный"},
    {"number": "+7 903 321 00 11", "price": 1500,  "operator": "Tele2",   "category": "Обычный"},
    {"number": "+7 999 888 88 88", "price": 20000, "operator": "МТС",     "category": "VIP"},
    {"number": "+7 977 000 11 00", "price": 4500,  "operator": "Билайн",  "category": "Красивый"},
]

CITIES = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск", "Краснодар", "Другой город"]

# ========== ГЛАВНОЕ МЕНЮ ==========
def main_keyboard():
    keyboard = [
        ["🔎 Найти номер"],
        ["⭐ Красивые номера", "💎 VIP номера"],
        ["📱 Операторы"],
        ["🎲 Случайный номер"],
        ["📞 Оформить номер"],
        ["ℹ️ О сервисе", "📋 Мои заявки"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== КАРТОЧКА НОМЕРА ==========
def format_number_card(n, index=None):
    stars = "⭐" if n["category"] == "Красивый" else "💎" if n["category"] == "VIP" else "📱"
    text = (
        f"{stars} *{n['number']}*\n"
        f"💰 Цена: *{n['price']:,} ₽*\n"
        f"📡 Оператор: {n['operator']}\n"
        f"🏷 Категория: {n['category']}"
    )
    buttons = []
    if index is not None:
        buttons.append([InlineKeyboardButton("💳 Оформить этот номер", callback_data=f"buy_{index}")])
    return text, InlineKeyboardMarkup(buttons) if buttons else None

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Добро пожаловать в *НомерМаркет*!\n\n"
        "📱 Каталог красивых номеров телефонов\n"
        "✅ SIM и eSIM\n"
        "🏪 Получение в салоне вашего города\n\n"
        "⚠️ *Важно:* для оформления номера потребуются паспортные данные — это обязательное требование оператора связи.\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ========== ПОИСК ==========
async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 *Поиск номера*\n\n"
        "Введите цифры для поиска.\nНапример: `777` или `999` или `0000`",
        parse_mode="Markdown"
    )
    return SEARCH

async def do_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip().replace(" ", "").replace("-", "")
    results = [n for n in NUMBERS if query in n["number"].replace(" ", "").replace("+7", "")]

    if not results:
        await update.message.reply_text(
            f"😔 По запросу *{query}* ничего не найдено.\n\nПопробуйте другие цифры.",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
        return ConversationHandler.END

    await update.message.reply_text(f"✅ Найдено номеров: *{len(results)}*", parse_mode="Markdown")
    for n in results[:5]:
        text, markup = format_number_card(n, NUMBERS.index(n))
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

    return ConversationHandler.END

# ========== КРАСИВЫЕ НОМЕРА ==========
async def beautiful_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nums = [n for n in NUMBERS if n["category"] == "Красивый"]
    await update.message.reply_text(f"⭐ *Красивые номера* — {len(nums)} шт.\n", parse_mode="Markdown")
    for n in nums:
        text, markup = format_number_card(n, NUMBERS.index(n))
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

# ========== VIP НОМЕРА ==========
async def vip_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nums = [n for n in NUMBERS if n["category"] == "VIP"]
    await update.message.reply_text(f"💎 *VIP номера* — {len(nums)} шт.\n", parse_mode="Markdown")
    for n in nums:
        text, markup = format_number_card(n, NUMBERS.index(n))
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

# ========== ОПЕРАТОРЫ ==========
async def operators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("МТС", callback_data="op_МТС"),
         InlineKeyboardButton("Билайн", callback_data="op_Билайн")],
        [InlineKeyboardButton("МегаФон", callback_data="op_МегаФон"),
         InlineKeyboardButton("Tele2", callback_data="op_Tele2")],
        [InlineKeyboardButton("СберМобайл", callback_data="op_СберМобайл")]
    ]
    await update.message.reply_text(
        "📡 *Выберите оператора:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def operator_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    op = query.data.replace("op_", "")
    nums = [n for n in NUMBERS if n["operator"] == op]
    if not nums:
        await query.message.reply_text(f"По оператору *{op}* номеров пока нет.", parse_mode="Markdown")
        return
    await query.message.reply_text(f"📱 *{op}* — найдено {len(nums)} номеров:", parse_mode="Markdown")
    for n in nums:
        text, markup = format_number_card(n, NUMBERS.index(n))
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=markup)

# ========== СЛУЧАЙНЫЙ НОМЕР ==========
async def random_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = random.choice(NUMBERS)
    i = NUMBERS.index(n)
    text, markup = format_number_card(n, i)
    await update.message.reply_text(
        "🎲 *Случайный номер для вас:*\n\n" + text,
        parse_mode="Markdown",
        reply_markup=markup
    )

# ========== О СЕРВИСЕ ==========
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *О НомерМаркет*\n\n"
        "📱 Более 450 000 красивых номеров\n"
        "✅ Официальное оформление у оператора\n"
        "💳 SIM и eSIM\n"
        "🏪 Получение в салоне вашего города\n"
        "📡 Операторы: МТС, Билайн, МегаФон, Tele2, СберМобайл\n\n"
        "*📄 Оформление номера:*\n"
        "Согласно Федеральному закону №126-ФЗ \"О связи\", все SIM-карты в России оформляются только по паспорту. "
        "Это обязательное требование — без паспортных данных оператор не активирует номер.\n\n"
        "Ваши данные используются исключительно для регистрации номера у оператора и никому не передаются.\n\n"
        "🔒 Конфиденциальность гарантирована.\n\n"
        "По всем вопросам: @Nomermarket\_support",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ========== МОИ ЗАЯВКИ ==========
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Мои заявки*\n\n"
        "История заказов появится после подключения базы данных.\n\n"
        "По статусу заявки обращайтесь к менеджеру.",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ========== ОФОРМЛЕНИЕ ЗАЯВКИ ==========
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        index = int(query.data.replace("buy_", ""))
        context.user_data["selected_number"] = NUMBERS[index]
        msg = query.message
    else:
        context.user_data["selected_number"] = None
        msg = update.message

    text = ""
    if context.user_data.get("selected_number"):
        n = context.user_data["selected_number"]
        text = f"Вы выбрали: *{n['number']}* — {n['price']:,} ₽\n\n"

    await msg.reply_text(
        text + "📝 *Оформление заявки*\n\n"
        "📄 После оплаты вам нужно будет прислать фото паспорта для оформления номера.\n\n"
        "Введите ваше имя:",
        parse_mode="Markdown"
    )
    return GET_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    keyboard = [[city] for city in CITIES]
    await update.message.reply_text(
        "🏙 Выберите ваш город:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return GET_CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    keyboard = [["📱 SIM-карта", "📲 eSIM"]]
    await update.message.reply_text(
        "Выберите тип:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return GET_SIMTYPE

async def get_simtype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["simtype"] = update.message.text
    await update.message.reply_text(
        "💬 Есть пожелания к номеру или комментарий? (или напишите «Нет»)",
        reply_markup=ReplyKeyboardMarkup([["Нет"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return GET_COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["comment"] = update.message.text
    d = context.user_data
    n = d.get("selected_number")
    number_text = f"*{n['number']}* — {n['price']:,} ₽" if n else "Не выбран (менеджер подберёт)"

    summary = (
        f"📋 *Проверьте заявку:*\n\n"
        f"👤 Имя: {d['name']}\n"
        f"🏙 Город: {d['city']}\n"
        f"📱 Тип: {d['simtype']}\n"
        f"📞 Номер: {number_text}\n"
        f"💬 Комментарий: {d['comment']}\n\n"
        f"Всё верно?"
    )
    keyboard = [["✅ Подтвердить", "❌ Отменить"]]
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRM

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "✅ Подтвердить":
        await update.message.reply_text("❌ Заявка отменена.", reply_markup=main_keyboard())
        context.user_data.clear()
        return ConversationHandler.END

    n = context.user_data.get("selected_number")
    price_text = f"{n['price']:,} ₽" if n else "по договорённости"

    keyboard = [
        [InlineKeyboardButton("📱 СБП (по номеру телефона)", callback_data="pay_sbp")],
        [InlineKeyboardButton("💳 Карта (реквизиты)", callback_data="pay_card")],
    ]
    await update.message.reply_text(
        f"💰 Сумма к оплате: *{price_text}*\n\n"
        f"Выберите способ оплаты:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PAYMENT_METHOD

async def payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = query.data

    n = context.user_data.get("selected_number")
    price_text = f"{n['price']:,} ₽" if n else "уточните у менеджера"

    if method == "pay_sbp":
        context.user_data["payment"] = "СБП"
        await query.message.reply_text(
            f"📱 *Оплата через СБП*\n\n"
            f"Переведите *{price_text}* на номер:\n\n"
            f"📞 `{SBP_PHONE}`\n"
            f"🏦 Банк: {CARD_BANK}\n"
            f"👤 Получатель: {CARD_NAME}\n\n"
            f"✅ После оплаты пришлите скриншот чека 👇",
            parse_mode="Markdown"
        )
    elif method == "pay_card":
        context.user_data["payment"] = "Карта"
        await query.message.reply_text(
            f"💳 *Оплата по реквизитам карты*\n\n"
            f"Переведите *{price_text}* на карту:\n\n"
            f"💳 `{CARD_NUMBER}`\n"
            f"🏦 Банк: {CARD_BANK}\n"
            f"👤 Получатель: {CARD_NAME}\n\n"
            f"✅ После оплаты пришлите скриншот чека 👇",
            parse_mode="Markdown"
        )

    return WAIT_SCREENSHOT

async def wait_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.user_data
    n = d.get("selected_number")
    number_text = f"{n['number']} — {n['price']:,} ₽" if n else "Не выбран"
    user = update.effective_user

    admin_text = (
        f"🔔 *НОВАЯ ОПЛАЧЕННАЯ ЗАЯВКА!*\n\n"
        f"👤 Имя: {d.get('name')}\n"
        f"🏙 Город: {d.get('city')}\n"
        f"📱 Тип: {d.get('simtype')}\n"
        f"📞 Номер: {number_text}\n"
        f"💬 Комментарий: {d.get('comment')}\n"
        f"💳 Способ оплаты: {d.get('payment')}\n\n"
        f"Telegram: @{user.username or 'нет'} (ID: `{user.id}`)"
    )

    try:
        await context.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
        if update.message.photo:
            await context.bot.send_photo(
                ADMIN_ID,
                update.message.photo[-1].file_id,
                caption="📎 Скриншот оплаты от покупателя"
            )
        elif update.message.document:
            await context.bot.send_document(
                ADMIN_ID,
                update.message.document.file_id,
                caption="📎 Скриншот оплаты от покупателя"
            )
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")

    await update.message.reply_text(
        "✅ *Оплата получена! Заявка принята.*\n\n"
        "Наш менеджер проверит платёж и свяжется с вами в ближайшее время.\n\n"
        "Спасибо, что выбрали НомерМаркет! 🎉",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Отменено.", reply_markup=main_keyboard())
    return ConversationHandler.END

# ========== ЗАПУСК ==========
app = ApplicationBuilder().token(TOKEN).build()

order_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📞 Оформить номер$"), order_start),
        CallbackQueryHandler(order_start, pattern="^buy_")
    ],
    states={
        GET_NAME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        GET_CITY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        GET_SIMTYPE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_simtype)],
        GET_COMMENT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        CONFIRM:         [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        PAYMENT_METHOD:  [CallbackQueryHandler(payment_method, pattern="^pay_")],
        WAIT_SCREENSHOT: [MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, wait_screenshot)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True
)

search_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^🔎 Найти номер$"), search_prompt)],
    states={
        SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_search)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True
)

app.add_handler(CommandHandler("start", start))
app.add_handler(order_conv)
app.add_handler(search_conv)
app.add_handler(MessageHandler(filters.Regex("^⭐ Красивые номера$"), beautiful_numbers))
app.add_handler(MessageHandler(filters.Regex("^💎 VIP номера$"), vip_numbers))
app.add_handler(MessageHandler(filters.Regex("^📱 Операторы$"), operators))
app.add_handler(MessageHandler(filters.Regex("^🎲 Случайный номер$"), random_number))
app.add_handler(MessageHandler(filters.Regex("^ℹ️ О сервисе$"), about))
app.add_handler(MessageHandler(filters.Regex("^📋 Мои заявки$"), my_orders))
app.add_handler(CallbackQueryHandler(operator_filter, pattern="^op_"))

print("✅ НомерМаркет бот запущен!")
app.run_polling()


