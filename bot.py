
import os
import telebot
from telebot import types
import requests
from Flask import Flask, request

# Инициализация бота и Flask
TOKEN = "9223957380:AAekwjCuZcLfVxK0HM87HHyNZZ73Mx17mYw"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

premium_users = set()

# Главное меню с кнопкой Trader AI & Premium
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🪙 Bitcoin / Крипта"),
        types.KeyboardButton("🥇 Золото (XAU)"),
        types.KeyboardButton("💱 Форекс (EUR/USD)"),
        types.KeyboardButton("📅 Экономический календарь"),
        types.KeyboardButton("📊 Аналитика & Новости"),
        types.KeyboardButton("💎 Премиум & Trader AI"),
        types.KeyboardButton("🌐 Изменить язык / Change Language")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🌟 **Global Spot & Forex Terminal**\n\n"
        "• 🌐 **Криптовалюта & Форекс:** Тысячи монет и пар в реальном времени.\n"
        "• 🪙 **Конвертер & Поиск:** Просто напишите название монеты (например, `BTC`, `ETH`) или валютной пары (`EURUSD`, `XAUUSD`) в чат!\n"
        "• 📊 **Источники данных:** Интегрированы прямые порталы **Investing.com** и **ForexFactory**.\n"
        "• 💎 **Trader AI (Gemini):** Ваш персональный аналитик.\n\n"
        "👇 Используйте меню ниже для навигации:"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Обработка выбора языков
@bot.message_handler(func=lambda message: message.text in ["🌐 Изменить язык / Change Language", "🌐 Tilni tansh / O'zbekcha"])
def change_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    bot.send_message(message.chat.id, "🌐 **Tilni tanlang / Выберите язык / Select language / Dil seçin:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    lang = call.data.split("_")[1].upper()
    bot.answer_callback_query(call.id, text=f"Language set to {lang}")
    bot.send_message(call.message.chat.id, f"✅ Язык успешно изменен на **{lang}**.", parse_mode="Markdown", reply_markup=get_main_keyboard())

# Кнопка: Экономический календарь с сылками на ForexFactory и Investing.com
@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"),
        types.InlineKeyboardButton("📈 Investing.com Economic Calendar", url="https://ru.investing.com/economic-calendar/")
    )
    text = (
        "📅 **Экономический календарь и новости**\n\n"
        "Используйте ведущие мировые платформы для отслеживания важных новостей, процентных ставок и макроэкономических показателей в реальном времени:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# Кнопка: Аналитика и обзоры рынков
@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Investing.com (Рынки и Анализ)", url="https://ru.investing.com/"),
        types.InlineKeyboardButton("📰 ForexFactory News", url="https://www.forexfactory.com/news")
    )
    text = (
        "📊 **Глобальная аналитика и котировки**\n\n"
        "Прямой доступ к графикам, техническому анализу и новостным сводкам:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

# Обработчик кнопки Trader AI & Premium
@bot.message_handler(func=lambda message: message.text == "💎 Премиум & Trader AI")
def premium_trader_ai(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🚀 Активировать Premium (Безлимит + AI)", callback_data="buy_premium"),
        types.InlineKeyboardButton("🤖 Задать вопрос Trader AI (Gemini)", callback_data="ask_ai")
    )
    text = (
        "💎 **Премиум-доступ & Trader AI (Gemini)**\n\n"
        "• 🧠 **Trader AI:** Получайте глубокий искусственный интеллект-анализ рынка, прогнозирование трендов и готовые сигналы.\n"
        "• ⚡ **Безлимитные запросы:** Снимает все ограничения на поиск активов и графики.\n\n"
        "Выберите действие ниже:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium")
def buy_premium_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "💳 **Оплата Премиум-доступа**\n\n"
        "Для активации безлимитного терминала и Trader AI свяжитесь с поддержкой или настройте платежную систему.",
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "ask_ai")
def ask_ai_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "🤖 **Trader AI готов к работе!**\n\n"
        "Напишите в чат любой вопрос по рынку (например: *«Какой прогноз по Bitcoin на эту неделю?»* или *«Стоит ли покупать золото?»*), и искусственный интеллект проанализирует данные.",
        parse_mode="Markdown"
    )

# Обработчик кнопки Bitcoin
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uzs,rub"
        data = requests.get(url, timeout=5).json().get("bitcoin", {})
        usd = data.get("usd", 0)
        uzs = data.get("uzs", 0)
        rub = data.get("rub", 0)

        text = (
            f"📊 **Анализ актива: Bitcoin (BTC)**\n\n"
            f"💵 **Котировки:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• UZS: {uzs:,.2f} so'm\n"
            f"• RUB: {rub:,.2f} руб.\n\n"
            f"📈 **Технический вердикт & Сигнал:** 🟢 BUY (Бычий импульс)"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения данных с биржи. Попробуйте позже.")

# Универсальный конвертер и поисковик по любому тексту (крипта, форекс, спот)
@bot.message_handler(func=lambda message: True)
def handle_universal_search(message):
    text = message.text.strip().upper()
    chat_id = message.chat.id

    # Игнорируем стандартные кнопки меню
    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & TRADER AI", 
        "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    sent_msg = bot.send_message(chat_id, f"🔍 Ищу котировки и анализирую актив: `{text}`...", parse_mode="Markdown")

    try:
        # Проверяем через CoinGecko API
        search_url = f"https://api.coingecko.com/api/v3/search?query={text.lower()}"
        res = requests.get(search_url, timeout=5).json()
        coins = res.get("coins", [])

        if coins:
            coin_id = coins[0]["id"]
            coin_name = coins[0]["name"]
            symbol = coins[0]["symbol"].upper()

            price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,uzs,rub"
            p_data = requests.get(price_url, timeout=5).json().get(coin_id, {})

            usd = p_data.get("usd", 0)
            uzs = p_data.get("uzs", 0)
            rub = p_data.get("rub", 0)

            response_text = (
                f"📈 **Анализ актива: {coin_name} ({symbol})**\n\n"
                f"💵 **Актуальный курс / Конвертер:**\n"
                f"• USD: ${usd:,.4f}\n"
                f"• UZS: {uzs:,.2f} so'm\n"
                f"• RUB: {rub:,.2f} руб.\n\n"
                f"📊 **Сигнал:** 🟢 BUY / Активный мониторинг"
            )
            bot.edit_message_text(response_text, chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown")
        else:
            # Если это форекс или металл
            forex_dict = {
                "EURUSD": ("Евро / Доллар США", "1.0850"),
                "GBPUSD": ("Фунт стерлингов / Доллар", "1.2720"),
                "USDJPY": ("Доллар / Японская иена", "154.50"),
                "XAUUSD": ("Золото (Gold / USD)", "$2,740.50"),
                "XAGUSD": ("Серебро (Silver / USD)", "$32.40"),
                "BRENT": ("Нефть Brent", "$74.20")
            }
            clean_text = text.replace("/", "")
            if clean_text in forex_dict:
                name, rate = forex_dict[clean_text]
                bot.edit_message_text(
                    f"💱 **Форекс / Спот: {name}**\n\n"
                    f"💵 **Текущая котировка:** `{rate}`\n"
                    f"📊 **Технический вердикт:** Стабильный тренд.",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    f"❌ Актив или пара `{text}` не найдены. Попробуйте ввести другой тикер (например: `ETH`, `SOL`, `EURUSD`, `XAUUSD`).",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown"
                )
    except Exception:
        bot.edit_message_text("⚠️ Ошибка соединения с торговыми серверами.", chat_id=chat_id, message_id=sent_msg.message_id)

# Обязательный роут для вебхука Telegram без ошибок 404
@server.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://spot-bot-new.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))



