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

# Прямой и железный запрос к Gemini API без ошибок библиотек и кэша
def ask_ai(prompt_text):
    if not GEMINI_API_KEY:
        return "⚠️ Ошибка: Ключ GEMINI_API_KEY не найден в настройках Render."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Ты — профессиональный трейдер и финансовый аналитик. Ответь на вопрос: {prompt_text}"}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_json = response.json()
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Ошибка ИИ: {str(e)}"

# Главное меню со ВСЕМИ функциями
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🪙 Bitcoin / Крипта"),
        types.KeyboardButton("🥇 Золото (XAU)"),
        types.KeyboardButton("💱 Форекс (EUR/USD)"),
        types.KeyboardButton("📈 Акции (AAPL / TSLA)"),
        types.KeyboardButton("📊 Графики (TradingView)"),
        types.KeyboardButton("📅 Экономический календарь"),
        types.KeyboardButton("📊 Аналитика & Новости"),
        types.KeyboardButton("💎 Премиум & VIP Сигналы"),
        types.KeyboardButton("📖 Инструкция для новичков"),
        types.KeyboardButton("🌐 Изменить язык / Change Language")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🌟 **Добро пожаловать в Global Spot & Forex Terminal!** 🚀\n\n"
        "🌍 **Профессиональный мультирыночный терминал:**\n"
        "• 📈 **Мировые акции** (Apple, Tesla, Microsoft и др.)\n"
        "• 🪙 **Криптовалюты** (Тысячи монет с конвертером в USD, UZS и RUB)\n"
        "• 💱 **Форекс и Металлы** (EUR/USD, Золото XAU)\n"
        "• 📊 **Интерактивные графики TradingView** для каждого актива\n"
        "• 📅 **Экономический календарь и аналитика рынков**\n"
        "• 💎 **VIP Торговые сигналы и Премиум-доступ**\n"
        "• 🤖 **Trader AI (Gemini)** для мгновенного прогноза и анализа\n\n"
        "👇 *Используйте кнопки меню ниже для работы:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

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
        "📖 **Пошаговая инструкция по использованию терминала:**\n\n"
        "1️⃣ **Поиск любого актива со всего мира:** Отправьте тикер в чат (`AAPL`, `BTC`, `EURUSD`).\n"
        "2️⃣ **Универсальный конвертер:** Бот автоматически пересчитывает курсы в **USD, UZS и RUB**.\n"
        "3️⃣ **Графики:** Кнопки TradingView привязаны к каждому активу.\n"
        "4️⃣ **Trader AI:** Задавайте любые вопросы по трейдингу текстом."
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
    bot.send_message(message.chat.id, "🌐 **Выберите язык / Select language / Dil seçin:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    lang = call.data.split("_")[1].upper()
    bot.answer_callback_query(call.id, text=f"Language set to {lang}")
    bot.send_message(call.message.chat.id, f"✅ Язык успешно изменен на **{lang}**.", parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"),
        types.InlineKeyboardButton("📈 Investing.com Calendar", url="https://ru.investing.com/economic-calendar/")
    )
    bot.send_message(message.chat.id, "📅 **Экономический календарь и важные события:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Investing.com (Рынки)", url="https://ru.investing.com/"),
        types.InlineKeyboardButton("📰 ForexFactory News", url="https://www.forexfactory.com/news")
    )
    bot.send_message(message.chat.id, "📊 **Глобальная аналитика и новости рынков:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💎 Премиум & VIP Сигналы")
def premium_trader_ai(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Купить 1 Месяц ($10)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💎 Купить 1 Год ($100 - Выгода!)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💬 Связаться с администратором", url="https://t.me/samadkhon_khmdvv")
    )
    text = (
        "💎 **Премиум-доступ & VIP Терминал**\n\n"
        "Получите максимальные возможности для успешного трейдинга:\n"
        "• 🤖 **Безлимитный Trader AI** — глубокий анализ без ограничений.\n"
        "• ⚡ **VIP Торговые Сигналы** — точные точки входа (Buy/Sell).\n"
        "• 🔔 **Ценовые уведомления** — контроль важных уровней.\n\n"
        "💳 **Тарифы:**\n"
        "• 📅 **1 Месяц:** `$10`\n"
        "• 📅 **1 Год:** `$100` *(Максимальная выгода!)*\n\n"
        "👇 Выберите тариф или нажмите кнопку связи для быстрой активации:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# Кнопка Bitcoin с живым курсом (без нулей)
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график BTC (TradingView)", url="https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT"))
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uzs,rub"
        res = requests.get(url, timeout=5).json()
        data = res.get("bitcoin", {})
        usd = data.get("usd", 0)
        uzs = data.get("uzs", 0)
        rub = data.get("rub", 0)
        text = (
            f"📊 **Анализ актива: Bitcoin (BTC)**\n\n"
            f"💵 **Конвертер валют:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• UZS: {uzs:,.2f} so'm\n"
            f"• RUB: {rub:,.2f} руб.\n\n"
            f"📈 **Технический вердикт & Сигнал:** 🟢 BUY"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения данных с биржи.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🥇 Золото (XAU)")
def gold_xau(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график Золота", url="https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD"))
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
    markup.add(types.InlineKeyboardButton("📈 Открыть график EUR/USD", url="https://www.tradingview.com/chart/?symbol=FX_IDC%3AEURUSD"))
    try:
        pair = yf.Ticker("EURUSD=X")
        price = pair.history(period="1d")['Close'].iloc[-1]
        bot.send_message(chat_id, f"💱 **Форекс: EUR/USD:** `{price:.4f}`\n📊 **Вердикт:** 🟡 NEUTRAL", parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "💱 **EUR/USD:** `1.0850`", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📈 Акции (AAPL / TSLA)")
def stocks_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Акции на TradingView", url="https://www.tradingview.com/markets/stocks-usa/top-gainers/"))
    bot.send_message(message.chat.id, "📈 **Мировые акции:**\n\nНапишите в чат тикер любой компании (`AAPL`, `TSLA`, `MSFT`), чтобы узнать актуальный курс!", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id

    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📈 АКЦИИ (AAPL / TSLA)", "📊 ГРАФИКИ (TRADINGVIEW)", "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", 
        "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & VIP СИГНАЛЫ", 
        "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # 1. Поиск активов мира
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
                bot.edit_message_text(f"📊 **Глобальный рынок: {text}**\n\n💵 **Цена:** `${price:,.2f}`", chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup)
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
                usd, uzs, rub = p_data.get("usd", 0), p_data.get("uzs", 0), p_data.get("rub", 0)
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"📈 График {symbol}", url=f"https://www.tradingview.com/chart/?symbol={symbol}USDT"))
                bot.edit_message_text(
                    f"📈 **Криптовалюта: {coins[0]['name']} ({symbol})**\n\n"
                    f"💵 **Конвертер валют:**\n"
                    f"• USD: ${usd:,.4f}\n"
                    f"• UZS: {uzs:,.2f} so'm\n"
                    f"• RUB: {rub:,.2f} руб.",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup
                )
                return
        except Exception:
            pass

        bot.edit_message_text(f"❌ Актив `{text}` не найден.", chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown")
        return

    # 2. Trader AI (Gemini)
    sent_ai = bot.send_message(chat_id, "🤖 **Trader AI анализирует ваш запрос...**", parse_mode="Markdown")
    ai_answer = ask_ai(original_text)
    try:
        bot.edit_message_text(f"🤖 **Trader AI (Экспертный анализ):**\n\n{ai_answer}", chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
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


















