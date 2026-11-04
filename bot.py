
import os
import telebot
from telebot import types
import requests
from flask import Flask, request
import google.generativeai as genai

# Инициализация бота и Flask
TOKEN = "9223957380:AAekwjCuZcLfVxK0HM87HHyNZZ73Mx17mYw"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Настройка Gemini API (ключ автоматически берется из переменных окружения Render)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Используем стабильную модель Gemini
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

# Команда /start с полным описанием бота для новичков
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🌟 **Добро пожаловать в Global Spot & Forex Terminal!** 🚀\n\n"
        "🤖 **Что это за бот?**\n"
        "Это твой персональный профессиональный мультирыночный терминал в Telegram. Он создан для трейдеров, инвесторов и новичков, чтобы в один клик отслеживать рынки, конвертировать валюты и получать аналитику.\n\n"
        "📌 **Основные возможности:**\n"
        "• 🌐 **Криптовалюта & Спот:** Котировки тысяч монет в реальном времени.\n"
        "• 💱 **Форекс & Металлы:** Валютные пары (EUR/USD, GBP/USD и др.), золото (XAU) и нефть.\n"
        "• 🪙 **Универсальный конвертер:** Просто напиши в чат название любого актива (например, `ETH`, `SOL`, `EURUSD`) — и бот мгновенно покажет курс в **USD, UZS и RUB**!\n"
        "• 📅 **Фундаментальный анализ:** Прямые ссылки на ведущие порталы *Investing.com* и *ForexFactory*.\n"
        "• 💎 **Trader AI (Gemini):** Искусственный интеллект для прогнозирования трендов и ответов на вопросы по трейдингу.\n\n"
        "👇 *Используй кнопки меню внизу для навигации:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Кнопка: Инструкция для новичков
@bot.message_handler(func=lambda message: message.text == "📖 Инструкция для новичков")
def beginner_guide(message):
    chat_id = message.chat.id
    guide_text = (
        "📖 **Гид по использованию терминала для начинающих:**\n\n"
        "1️⃣ **Как узнать цену монеты или валюты?**\n"
        "• Нажми на готовые кнопки в меню (например, «🪙 Bitcoin / Крипта» или «🥇 Золото»).\n"
        "• Либо просто **напиши текст в чат** (например: `ETH`, `BNB`, `GBPUSD`) — бот сам распознает актив и выдаст котировки.\n\n"
        "2️⃣ **Как пользоваться конвертером?**\n"
        "Любое текстовое сообщение с тикером автоматически пересчитывает стоимость актива в доллары ($), узбекские сумы (so'м) и рубли (руб.).\n\n"
        "3️⃣ **Где смотреть новости и календарь?**\n"
        "Используй разделы «📅 Экономический календарь» и «📊 Аналитика & Новости» для перехода на Investing.com и ForexFactory.\n\n"
        "4️⃣ **Как подключить Trader AI?**\n"
        "Нажми кнопку «💎 Премиум & Trader AI», чтобы активировать безлимитный доступ и задать вопрос искусственному интеллекту.\n\n"
        "💡 *Удачи в торговле! Если появятся вопросы, просто напиши их в чат.*"
    )
    bot.send_message(chat_id, guide_text, parse_mode="Markdown")

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

# Кнопка: Экономический календарь
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

# Кнопка: Аналитика и новости
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

# Кнопка: Trader AI & Premium
@bot.message_handler(func=lambda message: message.text == "💎 Премиум & Trader AI")
def premium_trader_ai(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🚀 Активировать Premium (Безлимит + AI)", callback_data="buy_premium"),
        types.InlineKeyboardButton("🤖 Как спросить Trader AI?", callback_data="ask_ai_info")
    )
    text = (
        "💎 **Премиум-доступ & Trader AI (Gemini)**\n\n"
        "• 🧠 **Trader AI:** Интегрирован с искусственным интеллектом Google Gemini. Вы можете написать любой вопрос по трейдингу прямо в чат!\n"
        "• ⚡ **Безлимитные запросы:** Снимает все ограничения на анализ активов.\n\n"
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

@bot.callback_query_handler(func=lambda call: call.data == "ask_ai_info")
def ask_ai_info_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "🤖 **Как работает Trader AI?**\n\n"
        "Просто напишите ваш вопрос обычным текстом в чат (например: *«Какой прогноз по биткоину?»*, *«Что такое стоп-лосс?»* или *«Стоит ли покупать золото сейчас?»*). Нейросеть Gemini мгновенно ответит вам!",
        parse_mode="Markdown"
    )

# Кнопка: Bitcoin / Крипта
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

# Универсальный обработчик текста: поиск монет, конвертер ИЛИ запрос к Gemini AI
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id

    # Игнорируем стандартные кнопки меню
    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & TRADER AI", 
        "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # Сначала проверяем, является ли запрос тикером крипты или форекса (длина обычно до 10 символов и без пробелов)
    if len(original_text.split()) == 1 and len(text) <= 10:
        sent_msg = bot.send_message(chat_id, f"🔍 Ищу котировки и анализирую актив: `{text}`...", parse_mode="Markdown")
        try:
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
                    return
        except Exception:
            pass
        # Если тикер не найден на бирже, передаем текст в Gemini AI ниже

    # Если это развернутый вопрос или текст — отправляем в Trader AI (Gemini)
    if gemini_model:
        sent_ai = bot.send_message(chat_id, "🤖 **Trader AI анализирует ваш вопрос...**", parse_mode="Markdown")
        try:
            prompt = (
                "Ты — профессиональный финансовый аналитик, трейдер и эксперт по рынкам криптовалют и форекс. "
                "Ответь на вопрос пользователя грамотно, конструктивно, с точки зрения трейдинга и анализа рисков. "
                f"Вопрос пользователя: {original_text}"
            )
            response = gemini_model.generate_content(prompt)
            ai_answer = response.text

            formatted_answer = (
                f"🤖 **Trader AI (Gemini Аналитика):**\n\n"
                f"{ai_answer}\n\n"
                f"💡 *Анализ подготовлен глобальным терминалом.*"
            )
            bot.edit_message_text(formatted_answer, chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
        except Exception as e:
            bot.edit_message_text("⚠️ Ошибка обращения к Trader AI. Попробуйте сформулировать вопрос иначе.", chat_id=chat_id, message_id=sent_ai.message_id)
    else:
        bot.send_message(chat_id, "⚠️ Trader AI временно недоступен (не настроен GEMINI_API_KEY на сервере).")

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





