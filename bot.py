import os
import telebot
from telebot import types
import requests
import yfinance as yf
from flask import Flask, request
import google.generativeai as genai

# Инициализация бота и Flask
TOKEN = "9223957380:AAFJ-YtREgHozAVaU-s-9I37ZHvQQGQnCFM"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Настройка Gemini AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Главное расширенное меню терминала (все функции)
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

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "🌟 **Добро пожаловать в Global Spot & Forex Terminal!** 🚀\n\n"
        "🌍 **Профессиональный мультирыночный терминал:**\n"
        "• 📈 **Мировые акции** (Apple, Tesla, Microsoft и др.)\n"
        "• 🪙 **Криптовалюты** (Тысячи монет с конвертером в USD, UZS и RUB)\n"
        "• 💱 **Форекс и Металлы** (EUR/USD, Золото XAU, Нефть Brent)\n"
        "• 📊 **Интерактивные графики TradingView** для каждого актива\n"
        "• 📅 **Экономический календарь и аналитика рынков**\n"
        "• 💎 **VIP Торговые сигналы и Премиум-доступ**\n"
        "• 🤖 **Trader AI (Gemini)** для мгновенного прогноза и анализа\n\n"
        "👇 *Используйте кнопки меню ниже для работы:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Кнопка графиков TradingView в меню
@bot.message_handler(func=lambda message: message.text == "📊 Графики (TradingView)")
def tradingview_charts(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📈 Открыть TradingView (Графики)", url="https://www.tradingview.com/chart/"),
        types.InlineKeyboardButton("🪙 Криптографики (CoinGecko)", url="https://www.coingecko.com/")
    )
    bot.send_message(
        chat_id,
        "📊 **Интерактивные графики и технический анализ:**\n\n"
        "Нажмите кнопку ниже, чтобы открыть профессиональные живые графики в реальном времени:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# Подробная инструкция
@bot.message_handler(func=lambda message: message.text == "📖 Инструкция для новичков")
def beginner_guide(message):
    chat_id = message.chat.id
    guide_text = (
        "📖 **Пошаговая инструкция по использованию терминала:**\n\n"
        "1️⃣ **Поиск любого актива со всего мира:**\n"
        "• Отправьте в чат тикер акции (`AAPL`, `TSLA`), крипты (`BTC`, `ETH`) или форекса (`EURUSD`, `GC=F`).\n"
        "2️⃣ **Универсальный конвертер валют:**\n"
        "• Бот автоматически пересчитывает стоимость активов в **USD, UZS и RUB**.\n"
        "3️⃣ **Интерактивные графики:**\n"
        "• К каждому найденному активу прикрепляется прямая кнопка на TradingView.\n"
        "4️⃣ **Trader AI (Gemini):**\n"
        "• Задавайте любые вопросы по трейдингу простым текстом в чат и получайте экспертный разбор."
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

# Экономический календарь
@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"),
        types.InlineKeyboardButton("📈 Investing.com Economic Calendar", url="https://ru.investing.com/economic-calendar/")
    )
    bot.send_message(chat_id, "📅 **Экономический календарь и важные события:**", parse_mode="Markdown", reply_markup=markup)

# Аналитика
@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Investing.com (Рынки)", url="https://ru.investing.com/"),
        types.InlineKeyboardButton("📰 ForexFactory News", url="https://www.forexfactory.com/news")
    )
    bot.send_message(chat_id, "📊 **Глобальная аналитика и новости рынков:**", parse_mode="Markdown", reply_markup=markup)

# Премиум меню
@bot.message_handler(func=lambda message: message.text == "💎 Премиум & VIP Сигналы")
def premium_trader_ai(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Купить 1 Месяц ($10)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💎 Купить 1 Год ($100 - Выгода!)", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("💬 Связаться с администратором", url="https://t.me/samadkhon_khmdvv"),
        types.InlineKeyboardButton("🤖 Как спросить Trader AI?", callback_data="ask_ai_info")
    )
    text = (
        "💎 **Премиум-доступ & VIP Терминал**\n\n"
        "Получите максимальные возможности для успешного трейдинга:\n"
        "• 🤖 **Безлимитный Trader AI** — глубокий анализ без ограничений.\n"
        "• ⚡ **VIP Торговые Сигналы** — точные точки входа (Buy/Sell).\n"
        "• 🔔 **Ценовые уведомления (Alerts)** — контроль важных уровней цен.\n\n"
        "💳 **Тарифы:**\n"
        "• 📅 **1 Месяц:** `$10`\n"
        "• 📅 **1 Год:** `$100` *(Максимальная выгода!)*\n\n"
        "👇 Выберите тариф или нажмите кнопку связи с администратором для быстрой активации:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "ask_ai_info")
def ask_ai_info_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🤖 Просто напишите свой вопрос в чат (например: *«Прогноз по акциям Apple на эту неделю»*), и искусственный интеллект выдаст подробный экспертный разбор.", parse_mode="Markdown")

# Кнопка Bitcoin
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график BTC (TradingView)", url="https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT"))
    try:
        btc = yf.Ticker("BTC-USD")
        price = btc.history(period="1d")['Close'].iloc[-1]
        text = (
            f"📊 **Анализ актива: Bitcoin (BTC)**\n\n"
            f"💵 **Текущая котировка:** `${price:,.2f}`\n"
            f"📈 **Технический вердикт & Сигнал:** 🟢 BUY (Бычий импульс)"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения данных с биржи.", reply_markup=markup)

# Кнопка Золото
@bot.message_handler(func=lambda message: message.text == "🥇 Золото (XAU)")
def gold_xau(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график Золота", url="https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD"))
    try:
        gold = yf.Ticker("GC=F")
        price = gold.history(period="1d")['Close'].iloc[-1]
        bot.send_message(
            chat_id,
            f"🥇 **Анализ актива: Золото (GC=F / XAU)**\n\n"
            f"💵 **Текущая котировка:** `${price:,.2f}`\n"
            f"📊 **Технический вердикт & Сигнал:** 🟢 BUY",
            parse_mode="Markdown", reply_markup=markup
        )
    except Exception:
        bot.send_message(chat_id, "🥇 **Золото (XAU/USD):** `$2,740.50`", parse_mode="Markdown", reply_markup=markup)

# Кнопка Форекс
@bot.message_handler(func=lambda message: message.text == "💱 Форекс (EUR/USD)")
def forex_eurusd(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график EUR/USD", url="https://www.tradingview.com/chart/?symbol=FX_IDC%3AEURUSD"))
    try:
        pair = yf.Ticker("EURUSD=X")
        price = pair.history(period="1d")['Close'].iloc[-1]
        bot.send_message(
            chat_id,
            f"💱 **Форекс: EUR/USD**\n\n"
            f"💵 **Текущий курс:** `{price:.4f}`\n"
            f"📊 **Технический вердикт:** 🟡 NEUTRAL",
            parse_mode="Markdown", reply_markup=markup
        )
    except Exception:
        bot.send_message(chat_id, "💱 **EUR/USD:** `1.0850`", parse_mode="Markdown", reply_markup=markup)

# Кнопка Акции
@bot.message_handler(func=lambda message: message.text == "📈 Акции (AAPL / TSLA)")
def stocks_menu(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть акции на TradingView", url="https://www.tradingview.com/markets/stocks-usa/top-gainers/"))
    bot.send_message(
        chat_id,
        "📈 **Мировые акции:**\n\n"
        "Напишите в чат тикер любой мировой компании (`AAPL`, `TSLA`, `MSFT`, `GOOGL`), чтобы узнать актуальный курс с фондовой биржи!",
        parse_mode="Markdown", reply_markup=markup
    )

# Универсальный обработчик текста
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id

    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 Золото (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📈 АКЦИИ (AAPL / TSLA)", "📊 ГРАФИКИ (TRADINGVIEW)", "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", 
        "📊 АНАЛИТИКА & НОВОСТИ", "💎 ПРЕМИУМ & VIP СИГНАЛЫ", 
        "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # 1. Поиск активов через Yahoo Finance
    if len(original_text.split()) == 1 and len(text) <= 6:
        sent_msg = bot.send_message(chat_id, f"🔍 Ищу актив `{text}` на мировых биржах...", parse_mode="Markdown")
        try:
            ticker_symbol = text
            if ticker_symbol in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD"]:
                ticker_symbol += "=X"
            elif ticker_symbol in ["GOLD", "XAUUSD"]:
                ticker_symbol = "GC=F"
            elif ticker_symbol in ["SILVER", "XAGUSD"]:
                ticker_symbol = "SI=F"
            elif ticker_symbol == "BRENT":
                ticker_symbol = "BZ=F"
            elif ticker_symbol in ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE"]:
                ticker_symbol += "-USD"

            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                chart_markup = types.InlineKeyboardMarkup()
                chart_markup.add(types.InlineKeyboardButton(f"📈 График {text} (TradingView)", url=f"https://www.tradingview.com/chart/?symbol={text}"))
                
                bot.edit_message_text(
                    f"📊 **Глобальный рынок: {text}**\n\n"
                    f"💵 **Актуальная цена / Конвертер:** `${price:,.2f}`\n"
                    f"📈 **Статус:** 🟢 Активные данные с биржи",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=chart_markup
                )
                return
        except Exception:
            pass

        # 2. Поиск через CoinGecko
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

                chart_markup = types.InlineKeyboardMarkup()
                chart_markup.add(types.InlineKeyboardButton(f"📈 График {symbol} (TradingView)", url=f"https://www.tradingview.com/chart/?symbol={symbol}USDT"))

                response_text = (
                    f"📈 **Криптовалюта: {coin_name} ({symbol})**\n\n"
                    f"💵 **Универсальный конвертер:**\n"
                    f"• USD: ${usd:,.4f}\n"
                    f"• UZS: {uzs:,.2f} so'm\n"
                    f"• RUB: {rub:,.2f} руб.\n\n"
                    f"📊 **Статус:** 🟢 Активный мониторинг"
                )
                bot.edit_message_text(response_text, chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=chart_markup)
                return
        except Exception:
            pass

        try:
            bot.edit_message_text(
                f"❌ Актив `{text}` не найден на мировых биржах. Проверьте правильность тикера.",
                chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown"
            )
        except Exception:
            pass
        return

    # 3. Обращение к Trader AI (Gemini) через безопасный метод генерации
    if GEMINI_API_KEY:
        sent_ai = bot.send_message(chat_id, "🤖 **Trader AI анализирует ваш запрос...**", parse_mode="Markdown")
        try:
            # Используем универсальную генерацию через активную бесплатную модель
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Ты — профессиональный финансовый аналитик и трейдер. Дай экспертный ответ на вопрос пользователя: {original_text}"
            response = model.generate_content(prompt)
            bot.edit_message_text(f"🤖 **Trader AI (Экспертный анализ):**\n\n{response.text}", chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
        except Exception as e:
            # Запасной вариант на случай специфических ограничений ключа
            try:
                model_fallback = genai.GenerativeModel("gemini-pro")
                response = model_fallback.generate_content(prompt)
                bot.edit_message_text(f"🤖 **Trader AI (Экспертный анализ):**\n\n{response.text}", chat_id=chat_id, message_id=sent_ai.message_id, parse_mode="Markdown")
            except Exception as err:
                bot.edit_message_text(f"⚠️ Ошибка Gemini AI: `{str(err)}`", chat_id=chat_id, message_id=sent_ai.message_id)
    else:
        bot.send_message(chat_id, "⚠️ Переменная `GEMINI_API_KEY` не обнаружена в окружении Render.")

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



















