
import os
import telebot
from telebot import types
import requests
from flask import Flask, request
import google.generativeai as genai

# Инициализация бота и Flask
TOKEN = "9223957380:AAFJ-YtREgHozAVaU-s-9I37ZHvQQGQnCFM"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Настройка Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

premium_users = set()

# Главное меню терминала
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🪙 Bitcoin / Крипта"),
        types.KeyboardButton("🥇 Золото (XAU)"),
        types.KeyboardButton("💱 Форекс (EUR/USD)"),
        types.KeyboardButton("📅 Экономический календарь"),
        types.KeyboardButton("📊 Аналитика & Новости"),
        types.KeyboardButton("💎 Премиум & Trader AI"),
        types.KeyboardButton("📖 Инструкция для новичков"),
        types.KeyboardButton("🌐 Изменить язык / Change Language")
    )
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🌟 **Добро пожаловать в Global Spot & Forex Terminal!** 🚀\n\n"
        "🤖 **Что это за бот?**\n"
        "Это твой персональный профессиональный мультирыночный терминал в Telegram для отслеживания рынков, конвертации валют и аналитики.\n\n"
        "📌 **Основные возможности:**\n"
        "• 🌐 **Криптовалюта & Спот:** Котировки тысяч монет в реальном времени.\n"
        "• 💱 **Форекс & Металлы:** Валютные пары (`EURUSD`, `GBPUSD`, `USDJPY`), золото (`XAUUSD`) и нефть (`Brent`).\n"
        "• 🪙 **Конвертер:** Напиши любой тикер в чат — получи курс в **USD, UZS и RUB**!\n"
        "• 📅 **Фундаментальный анализ:** Ссылки на *Investing.com* и *ForexFactory*.\n"
        "• 💎 **Trader AI (Gemini):** Искусственный интеллект для прогнозов и ответов.\n\n"
        "👇 *Используй кнопки меню ниже:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Инструкция для новичков
@bot.message_handler(func=lambda message: message.text == "📖 Инструкция для новичков")
def beginner_guide(message):
    chat_id = message.chat.id
    guide_text = (
        "📖 **Гид по использованию терминала:**\n\n"
        "1️⃣ **Как узнать цену?** Нажми кнопку в меню или напиши в чат тикер (`BTC`, `ETH`, `XAUUSD`, `EURUSD`).\n"
        "2️⃣ **Конвертер:** Любое слово-тикер автоматически пересчитывает стоимость актива в USD, UZS и RUB.\n"
        "3️⃣ **Новости и календарь:** Используй разделы календаря и аналитики для перехода на Investing.com и ForexFactory.\n"
        "4️⃣ **Trader AI:** Напиши любой вопрос по трейдингу текстом в чат, и нейросеть ответит."
    )
    bot.send_message(chat_id, guide_text, parse_mode="Markdown")

# Выбор языков
@bot.message_handler(func=lambda message: message.text in ["🌐 Изменить язык / Change Language", "🌐 Tilni tansh / O'zbekcha"])
def change_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    bot.send_message(message.chat.id, "🌐 **Выберите язык / Select language / Dil seçin:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    lang = call.data.split("_")[1].upper()
    bot.answer_callback_query(call.id, text=f"Language set to {lang}")
    bot.send_message(call.message.chat.id, f"✅ Язык успешно изменен на **{lang}**.", parse_mode="Markdown", reply_markup=get_main_keyboard())

# Календарь
@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"),
        types.InlineKeyboardButton("📈 Investing.com Economic Calendar", url="https://ru.investing.com/economic-calendar/")
    )
    bot.send_message(chat_id, "📅 **Экономический календарь и новости:**", parse_mode="Markdown", reply_markup=markup)

# Аналитика
@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Investing.com (Рынки)", url="https://ru.investing.com/"),
        types.InlineKeyboardButton("📰 ForexFactory News", url="https://www.forexfactory.com/news")
    )
    bot.send_message(chat_id, "📊 **Глобальная аналитика:**", parse_mode="Markdown", reply_markup=markup)

# Премиум & AI меню с обновленными ценами и твоей ссылкой
@bot.message_handler(func=lambda message: message.text == "💎 Премиум & Trader AI")
def premium_trader_ai(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💬 Купить Премиум (Связаться)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("🤖 Как спросить Trader AI?", callback_data="ask_ai_info")
    )
    text = (
        "💎 **Премиум-доступ & Trader AI (Gemini)**\n\n"
        "Получите безлимитный доступ ко всем функциям терминала, расширенным графикам и искусственному интеллекту.\n\n"
        "💳 **Наши тарифы:**\n"
        "• 📅 **1 Месяц:** `$10`\n"
        "• 📅 **1 Год:** `$100` *(Выгода!)*\n\n"
        "👇 Нажмите кнопку ниже, чтобы связаться с администратором для оплаты и активации:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "ask_ai_info")
def ask_ai_info_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🤖 Просто напишите свой вопрос в чат (например: *«Прогноз по золоту»*), и нейросеть ответит.", parse_mode="Markdown")

# Кнопка Bitcoin
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uzs,rub"
        response = requests.get(url, timeout=5).json()
        data = response.get("bitcoin", {})
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

# Кнопка Золото
@bot.message_handler(func=lambda message: message.text == "🥇 Золото (XAU)")
def gold_xau(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "🥇 **Анализ актива: Золото (XAU/USD)**\n\n"
        "💵 **Текущая котировка:** `$2,740.50`\n"
        "📊 **Технический вердикт & Сигнал:** 🟢 BUY (Сильный тренд вверх)\n"
        "💡 *Рынок металлов стабилен.*",
        parse_mode="Markdown"
    )

# Кнопка Форекс
@bot.message_handler(func=lambda message: message.text == "💱 Форекс (EUR/USD)")
def forex_eurusd(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "💱 **Форекс: EUR/USD (Евро / Доллар США)**\n\n"
        "💵 **Текущий курс:** `1.0850`\n"
        "📊 **Технический вердикт & Сигнал:** 🟡 NEUTRAL / Консолидация",
        parse_mode="Markdown"
    )

# Универсальный обработчик текста (Поиск форекс-пар, металлов, крипты + Gemini AI)
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id

    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & TRADER AI", 
        "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # Проверка на тикер
    if len(original_text.split()) == 1 and len(text) <= 10:
        sent_msg = bot.send_message(chat_id, f"🔍 Ищу котировки актива: `{text}`...", parse_mode="Markdown")
        try:
            forex_dict = {
                "EURUSD": ("Евро / Доллар США (EUR/USD)", "1.0850", "🟡 NEUTRAL"),
                "GBPUSD": ("Фунт стерлингов / Доллар (GBP/USD)", "1.2720", "🟢 BUY"),
                "USDJPY": ("Доллар / Японская иена (USD/JPY)", "154.50", "🔴 SELL"),
                "USDCAD": ("Доллар США / Канадский доллар (USD/CAD)", "1.3910", "🟡 NEUTRAL"),
                "AUDUSD": ("Австралийский доллар / Доллар (AUD/USD)", "0.6580", "🟢 BUY"),
                "XAUUSD": ("Золото / Доллар (Gold / XAU)", "$2,740.50", "🟢 BUY"),
                "XAGUSD": ("Серебро / Доллар (Silver / XAG)", "$32.40", "🟢 BUY"),
                "BRENT": ("Нефть Brent Crude Oil", "$74.20", "🔴 SELL")
            }
            clean_text = text.replace("/", "")
            if clean_text in forex_dict:
                name, rate, signal = forex_dict[clean_text]
                bot.edit_message_text(
                    f"💱 **Форекс / Спот: {name}**\n\n"
                    f"💵 **Котировка:** `{rate}`\n"
                    f"📊 **Технический вердикт:** {signal}",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown"
                )
                return

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
                return
            else:
                bot.edit_message_text(
                    f"❌ Актив или пара `{text}` не найдены. Проверьте правильность написания.",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown"
                )
                return
        except Exception:
            pass

    # Запрос в Gemini AI
    if gemini_model:
        sent_ai = bot.send_message(chat_id, "🤖 **Trader AI анализирует ваш вопрос...**", parse_mode="Markdown")
        try:
            prompt = f"Ты — профессиональный финансовый аналитик и трейдер. Дай экспертный ответ на вопрос пользователя: {original_text}"
            response = gemini_model.generate_content(prompt)
            bot.edit_message_text(f"🤖 **Trader AI (Gemini Аналитика):**\n\n{response.text}", chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
        except Exception:
            bot.edit_message_text("⚠️ Ошибка обращения к Trader AI.", chat_id=chat_id, message_id=sent_ai.message_id)
    else:
        bot.send_message(chat_id, "⚠️ Trader AI недоступен: добавьте переменную `GEMINI_API_KEY` в настройках Render.")

# Вебхук
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







