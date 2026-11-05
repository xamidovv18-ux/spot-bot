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

# Главное расширенное меню терминала
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

# Кнопка Bitcoin (с встроенным конвертером в USD, UZS, RUB)
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график BTC (TradingView)", url="https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT"))
    try:
        # Запрашиваем цены в USD, UZS и RUB напрямую через CoinGecko для стабильности
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uzs,rub"
        response = requests.get(url, timeout=5).json()
        data = response.get("bitcoin", {})
        usd = data.get("usd", 0)
        uzs = data.get("uzs", 0)
        rub = data.get("rub", 0)

        text = (
            f"📊 **Анализ актива: Bitcoin (BTC)**\n\n"
            f"💵 **Конвертер валют:**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• UZS: {uzs:,.2f} so'm\n"
            f"• RUB: {rub:,.2f} руб.\n\n"
            f"📈 **Технический вердикт & Сигнал:** 🟢 BUY (Бычий импульс)"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения данных с биржи.", reply_markup=markup)

# Универсальный обработчик текста (Любой актив мира + Конвертер + Trader AI)
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

    # 1. Поиск активов мира через Yahoo Finance (акции, форекс, сырье, крипта)
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
                    f"💵 **Актуальная цена:** `${price:,.2f}`\n"
                    f"📈 **Статус:** 🟢 Активные данные с биржи",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=chart_markup
                )
                return
        except Exception:
            pass

        # 2. Поиск криптовалют и конвертер (с встроенным UZS и RUB) через CoinGecko
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
                    f"💵 **Конвертер валют:**\n"
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

    # 3. Обращение к Trader AI (Gemini) без ошибок
    if GEMINI_API_KEY:
        sent_ai = bot.send_message(chat_id, "🤖 **Trader AI анализирует ваш запрос...










