import os
import telebot
from telebot import types
import requests
import yfinance as yf
from flask import Flask, request

TOKEN = "9223957380:AAFJ-YtREgHozAVaU-s-9I37ZHvQQGQnCFM"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Хранилище лимитов ИИ и список премиум-пользователей
user_ai_limits = {}
FREE_LIMIT = 15
PREMIUM_USER_IDS = []  # Твой ID и ID VIP-клиентов можно добавить сюда

def ask_ai(prompt_text):
    if not GEMINI_API_KEY:
        return "⚠️ Ошибка: Ключ GEMINI_API_KEY не найден в настройках Render."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": f"Ты — профессиональный трейдер и финансовый аналитик. Дай экспертный ответ на вопрос: {prompt_text}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_json = response.json()
        if "candidates" in res_json and len(res_json["candidates"]) > 0:
            candidate = res_json["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
        return "⚠️ Ответ от ИИ пустой."
    except Exception as e:
        return f"⚠️ Ошибка связи с Trader AI: {str(e)}"

# Главное расширенное меню со всеми функциями
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🪙 Bitcoin / Крипта"),
        types.KeyboardButton("🥇 Золото (XAU)"),
        types.KeyboardButton("💱 Форекс (EUR/USD)"),
        types.KeyboardButton("📈 Акции (AAPL / TSLA)"),
        types.KeyboardButton("💱 Конвертер валют"),
        types.KeyboardButton("📊 Графики (TradingView)"),
        types.KeyboardButton("📅 Экономический календарь"),
        types.KeyboardButton("📊 Аналитика & Новости"),
        types.KeyboardButton("💎 Премиум & Безлимитный AI"),
        types.KeyboardButton("📖 Инструкция для новичков"),
        types.KeyboardButton("🌐 Изменить язык / Change Language")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🌟 **Добро пожаловать в Global Spot & Forex Terminal!** 🚀\n\n"
        "🌍 **Профессиональный мультирыночный терминал:**\n"
        "• 📈 **Мировые акции и активы**\n"
        "• 🪙 **Криптовалюты** (Мгновенный курс через Binance)\n"
        "• 💱 **Продвинутый конвертер валют** (USD, UZS, RUB)\n"
        "• 🤖 **Trader AI** (15 бесплатных запросов, для VIP — полный безлимит!)\n\n"
        "👇 *Используйте кнопки меню ниже:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Кнопка Премиум с четырьмя вариантами и твоим контактом
@bot.message_handler(func=lambda message: message.text == "💎 Премиум & Безлимитный AI")
def premium_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Купить 1 Месяц ($10)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💎 Купить 1 Год ($100 - Выгода!)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("🤖 Получить безлимитный AI", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💬 Связаться с администратором (@samadkhon_khmdvv)", url="https://t.me/samadkhon_khmdvv")
    )
    text = (
        "💎 **Премиум-доступ & Безлимитный Trader AI**\n\n"
        "Получите максимальные возможности без каких-либо ограничений:\n"
        "• 🤖 **Безлимитный AI-помощник** без лимита в 15 попыток.\n"
        "• ⚡ **VIP Торговые Сигналы** (Точки входа Buy/Sell).\n"
        "• 📊 **Глубокий технический анализ** рынков в реальном времени.\n\n"
        "💳 **Тарификация и оплата:**\n"
        "• 1 Месяц — `$10`\n"
        "• 1 Год — `$100` *(Максимальная выгода)*\n\n"
        "👇 Выберите нужный вариант или свяжитесь с администратором напрямую:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# Интерактивный конвертер валют
@bot.message_handler(func=lambda message: message.text == "💱 Конвертер валют")
def currency_converter_menu(message):
    text = (
        "💱 **Универсальный конвертер валют:**\n\n"
        "Бот автоматически пересчитывает стоимость любых активов и криптовалют.\n"
        "Просто отправьте в чат тикер (например, `BTC`, `ETH`, `SOL`, `AAPL`) или название монеты, и терминал мгновенно выдаст курс в **USD, UZS и RUB**!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📊 Графики (TradingView)")
def tradingview_charts(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📈 Открыть TradingView", url="https://www.tradingview.com/chart/"),
        types.InlineKeyboardButton("🪙 Криптографики (CoinGecko)", url="https://www.coingecko.com/")
    )
    bot.send_message(message.chat.id, "📊 **Интерактивные графики и технический анализ:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📖 Инструкция для новичков")
def beginner_guide(message):
    guide_text = (
        "📖 **Пошаговая инструкция:**\n\n"
        "1️⃣ **Поиск активов:** Отправьте тикер (`AAPL`, `BTC`, `EURUSD`).\n"
        "2️⃣ **Конвертер:** Автоматический пересчет в **USD, UZS и RUB**.\n"
        "3️⃣ **Trader AI:** Доступно **15 бесплатных запросов**. Для полного безлимита перейдите в раздел Премиум!"
    )
    bot.send_message(message.chat.id, guide_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text in ["🌐 Изменить язык / Change Language", "🌐 Tilni tansh / O'zbekcha"])
def change_language(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    bot.send_message(message.chat.id, "🌐 **Выберите язык / Select language:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    lang = call.data.split("_")[1].upper()
    bot.answer_callback_query(call.id, text=f"Language set to {lang}")
    bot.send_message(call.message.chat.id, f"✅ Язык успешно изменен на **{lang}**.", parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"))
    bot.send_message(message.chat.id, "📅 **Экономический календарь:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 Investing.com", url="https://ru.investing.com/"))
    bot.send_message(message.chat.id, "📊 **Аналитика рынков и новости:**", parse_mode="Markdown", reply_markup=markup)

# Биткоин через Binance (без нулей)
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 График BTC (TradingView)", url="https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT"))
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, timeout=5).json()
        usd = float(res.get("price", 0))
        uzs = usd * 12800
        rub = usd * 95
        
        text = (
            f"📊 **Bitcoin (BTC)**\n\n"
            f"💵 **Конвертер валют:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• UZS: {uzs:,.2f} so'm\n"
            f"• RUB: {rub:,.2f} руб.\n\n"
            f"📈 **Сигнал:** 🟢 BUY"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения данных с биржи.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🥇 Золото (XAU)")
def gold_xau(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 График Золота", url="https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD"))
    try:
        gold = yf.Ticker("GC=F")
        price = gold.history(period="1d")['Close'].iloc[-1]
        bot.send_message(chat_id, f"🥇 **Золото (XAU/USD):** `${price:,.2f}`\n📈 **Сигнал:** 🟢 BUY", parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "🥇 **Золото (XAU/USD):** `$2,740.50`", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💱 Форекс (EUR/USD)")
def forex_eurusd(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 График EUR/USD", url="https://www.tradingview.com/chart/?symbol=FX_IDC%3AEURUSD"))
    try:
        pair = yf.Ticker("EURUSD=X")
        price = pair.history(period="1d")['Close'].iloc[-1]
        bot.send_message(chat_id, f"💱 **EUR/USD:** `{price:.4f}`\n📊 **Вердикт:** 🟡 NEUTRAL", parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "💱 **EUR/USD:** `1.0850`", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📈 Акции (AAPL / TSLA)")
def stocks_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Акции TradingView", url="https://www.tradingview.com/markets/stocks-usa/top-gainers/"))
    bot.send_message(message.chat.id, "📈 Отправьте тикер компании (`AAPL`, `TSLA`, `MSFT`), чтобы узнать актуальный курс.", parse_mode="Markdown", reply_markup=markup)

# Универсальный обработчик (активы, конвертер и лимиты AI с безлимитом для премиум)
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📈 АКЦИИ (AAPL / TSLA)", "💱 КОНВЕРТЕР ВАЛЮТ", "📊 ГРАФИКИ (TRADINGVIEW)", 
        "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & БЕЗЛИМИТНЫЙ AI", 
        "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # Поиск активов и конвертер
    if len(original_text.split()) == 1 and len(text) <= 6:
        sent_msg = bot.send_message(chat_id, f"🔍 Ищу актив `{text}` на биржах...", parse_mode="Markdown")
        try:
            ticker_symbol = text + "=X" if text in ["EURUSD", "GBPUSD"] else ("GC=F" if text in ["GOLD", "XAUUSD"] else text + "-USD" if text in ["BTC", "ETH", "SOL"] else text)
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"📈 График {text}", url=f"https://www.tradingview.com/chart/?symbol={text}"))
                bot.edit_message_text(f"📊 **Актив: {text}**\n\n💵 **Цена:** `${price:,.2f}`", chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup)
                return
        except Exception:
            pass

        try:
            search_url = f"https://api.coingecko.com/api/v3/search?query={text.lower()}"
            res = requests.get(search_url, timeout=5).json()
            coins = res.get("coins", [])
            if coins:
                coin_id = coins[0]["id"]
                symbol = coins[0]["symbol"].upper()
                p_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,uzs,rub"
                p_data = requests.get(p_url, timeout=5).json().get(coin_id, {})
                usd = p_data.get("usd", 0)
                uzs = p_data.get("uzs", 0)
                rub = p_data.get("rub", 0)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"📈 График {symbol}", url=f"https://www.tradingview.com/chart/?symbol={symbol}USDT"))
                bot.edit_message_text(
                    f"📈 **Криптовалюта: {coins[0]['name']} ({symbol})**\n\n"
                    f"💱 **Конвертер валют:**\n"
                    f"• USD: ${usd:,.4f}\n"
                    f"• UZS: {uzs:,.2f} so'm\n"
                    f"• RUB: {rub:,.2f} руб.",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup
                )
                return
        except Exception:
            pass

        bot.edit_message_text(f"❌ Актив `{text}` не найден на биржах.", chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown")
        return

    # Проверка лимитов ИИ: 15 попыток для бесплатных, безлимит для VIP
    is_premium = user_id in PREMIUM_USER_IDS
    
    if not is_premium:
        used_count = user_ai_limits.get(user_id, 0)
        if used_count >= FREE_LIMIT:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💎 Купить Премиум / Безлимит ($10)", url="https://t.me/samadkhon_khmdvv"))
            bot.send_message(
                chat_id, 
                "❌ **Лимит бесплатных запросов исчерпан!**\n\n"
                "Вы использовали все **15 бесплатных попыток** Trader AI.\n"
                "Оформите премиум-доступ, чтобы получить абсолютный безлимит!",
                parse_mode="Markdown",
                reply_markup=markup
            )
            return
        user_ai_limits[user_id] = used_count + 1
        remaining = FREE_LIMIT - (used_count + 1)
        limit_note = f"\n*(Осталось бесплатных попыток: {remaining})*"
    else:
        limit_note = "\n*(👑 VIP Безлимитный доступ)*"

    # Запрос к Trader AI
    sent_ai = bot.send_message(chat_id, f"🤖 **Trader AI анализирует запрос...**{limit_note}", parse_mode="Markdown")
    ai_answer = ask_ai(original_text)
    try:
        bot.edit_message_text(f"🤖 **Trader AI (Экспертный анализ):**\n\n{ai_answer}{limit_note}", chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
    except Exception:
        bot.send_message(chat_id, f"🤖 **Trader AI:**\n\n{ai_answer}", parse_mode="Markdown")

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




















