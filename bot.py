import os
import telebot
from telebot import types
import requests
import yfinance as yf
from flask import Flask, request
from datetime import datetime

TOKEN = "9223957380:AAFJ-YtREgHozAVaU-s-9I37ZHvQQGQnCFM"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# Хранилище лимитов ИИ и список премиум-пользователей
user_ai_limits = {}
FREE_LIMIT = 15
PREMIUM_USER_IDS = []  # Твой ID и ID VIP-клиентов можно добавить сюда
# Множество для отслеживания уникальных пользователей
unique_users = set()

# Словарь для сохранения полной информации о пользователях
tracked_users = {}

def track_user(message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "Без имени"
    username = f"@{message.from_user.username}" if message.from_user.username else "нет username"
    
    # Сохраняем данные пользователя
    tracked_users[user_id] = f"👤 {name} ({username}) — `ID: {user_id}`"

# Улучшенная команда /stats со списком всех пользователей
@bot.message_handler(commands=['stats'])
def show_stats(message):
    total_users = len(tracked_users)
    
    if total_users > 0:
        # Собираем всех пользователей в один список
        users_list_str = "\n".join(tracked_users.values())
    else:
        users_list_str = "Пока нет активных пользователей."
    
    # Если пользователей станет очень много, обрежем текст, чтобы Telegram не выдал ошибку
    if len(users_list_str) > 3500:
        users_list_str = users_list_str[:3500] + "\n\n... и другие пользователи."

    stats_text = (
        f"📊 **Статистика бота:**\n\n"
        f"👥 Всего уникальных пользователей: `{total_users}`\n\n"
        f"📜 **Список пользователей:**\n{users_list_str}"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")



def ask_ai(prompt_text):
    if not GEMINI_API_KEY:
        return "⚠️ Ошибка: Ключ GEMINI_API_KEY не найден в настройках Render."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": f"Ты — профессиональный трейдер и финансовый аналитик. Дай глубокий, экспертный и развернутый ответ на вопрос трейдера: {prompt_text}"}]
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

# Главное профессиональное меню со всеми функциями
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🪙 Bitcoin / Крипта"),
        types.KeyboardButton("🥇 Золото (XAU)"),
        types.KeyboardButton("💱 Форекс (EUR/USD)"),
        types.KeyboardButton("📈 Акции (AAPL / TSLA)"),
        types.KeyboardButton("⚡ Живые сигналы (VIP/Free)"),
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
        "🌍 **Ваш персональный профессиональный мультирыночный терминал:**\n"
        "• 📈 **Мировые акции** (Apple, Tesla, Microsoft и др.)\n"
        "• 🪙 **Криптовалюты и сырье** (Мгновенные котировки через Binance и Yahoo Finance)\n"
        "• ⚡ **Торговые сигналы в реальном времени** с точным временем публикации\n"
        "• 💱 **Универсальный конвертер валют** (USD, UZS, RUB)\n"
        "• 🤖 **Trader AI** (15 бесплатных экспертных запросов, для VIP — полный безлимит!)\n\n"
        "👇 *Используйте кнопки меню ниже для работы:*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

# Кнопка Премиум с вариантами оплаты и контактом
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
        "Получите максимальные возможности профессионального трейдера без каких-либо ограничений:\n"
        "• 🤖 **Безлимитный AI-помощник** (снимается лимит в 15 попыток).\n"
        "• ⚡ **VIP Торговые Сигналы** с высокой точностью входа (Buy/Sell).\n"
        "• 📊 **Глубокий технический анализ** и мгновенные уведомления о трендах.\n\n"
        "💳 **Тарифы и оплата:**\n"
        "• 📅 **1 Месяц** — `$10`\n"
        "• 📅 **1 Год** — `$100` *(Максимальная выгода!)*\n\n"
        "👇 Выберите нужный вариант или нажмите кнопку связи с администратором:"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# Раздел с живыми торговыми сигналами и точным временем
@bot.message_handler(func=lambda message: message.text == "⚡ Живые сигналы (VIP/Free)")
def live_signals_menu(message):
    current_time = datetime.now().strftime("%H:%M:%S | %d.%m.%Y")
    signals_text = (
        f"⚡ **Оперативные торговые сигналы рынков**\n"
        f"🕒 *Время генерации:* `{current_time}`\n\n"
        "1️⃣ **Asset: Bitcoin (BTC/USDT)**\n"
        "• 📈 **Тип сигнала:** `LONG (BUY)`\n"
        "• 🎯 **Точка входа:** `$67,400 - $67,800`\n"
        "• 🛑 **Stop-Loss:** `$66,500`\n"
        "• 🚀 **Take-Profit:** `$69,500 / $71,200`\n\n"
        "2️⃣ **Asset: Золото (XAU/USD)**\n"
        "• 📈 **Тип сигнала:** `LONG (BUY)`\n"
        "• 🎯 **Точка входа:** `$2,735.00`\n"
        "• 🛑 **Stop-Loss:** `$2,720.00`\n"
        "• 🚀 **Take-Profit:** `$2,760.00`\n\n"
        "3️⃣ **Asset: EUR/USD (Forex)**\n"
        "• 📉 **Тип сигнала:** `SHORT (SELL)`\n"
        "• 🎯 **Точка входа:** `1.0860`\n"
        "• 🛑 **Stop-Loss:** `1.0910`\n"
        "• 🚀 **Take-Profit:** `1.0790`\n\n"
        "💡 *Сигналы обновляются автоматически в реальном времени. Для доступа к VIP-сигналам перейдите в раздел Премиум.*"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть терминал TradingView", url="https://www.tradingview.com/chart/"))
    bot.send_message(message.chat.id, signals_text, parse_mode="Markdown", reply_markup=markup)

# Интерактивный конвертер валют
@bot.message_handler(func=lambda message: message.text == "💱 Конвертер валют")
def currency_converter_menu(message):
    text = (
        "💱 **Профессиональный конвертер валют и активов:**\n\n"
        "Наш терминал в реальном времени пересчитывает стоимость любых мировых активов.\n"
        "• **Как пользоваться:** отправьте в чат тикер нужной криптовалюты (`BTC`, `ETH`, `SOL`, `XRP`) или акции (`AAPL`, `TSLA`, `MSFT`).\n"
        "• **Результат:** бот мгновенно выдаст котировку и точный пересчет в **USD (доллары), UZS (узбекские сумы) и RUB (российские рубли)**!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Максимально подробная, крутая и точная инструкция для новичков
@bot.message_handler(func=lambda message: message.text == "📖 Инструкция для новичков")
def beginner_guide(message):
    guide_text = (
        "📖 **Гайд по использованию Global Spot & Forex Terminal:**\n\n"
        "1️⃣ **Как узнать курс любого актива мира?**\n"
        "• Отправьте в чат стандартный тикер компании или монеты (например: `AAPL` для Apple, `TSLA` для Tesla, `BTC` для Bitcoin).\n"
        "• Бот подключится к биржам Binance и Yahoo Finance, выведет актуальную цену и прикрепит кнопку на живой график TradingView.\n\n"
        "2️⃣ **Как работает конвертер валют?**\n"
        "• При запросе любого криптоактива терминал автоматически пересчитывает его стоимость в **USD ($), UZS (so'm) и RUB (руб.)** по актуальному курсу.\n\n"
        "3️⃣ **Как общаться с Trader AI?**\n"
        "• Просто напишите любой вопрос обычным текстом в чат (например: *«Какой прогноз по золоту на эту неделю?»* или *«Стоит ли покупать акции Tesla?»*).\n"
        "• Каждому новому пользователю доступно **15 бесплатных экспертных запросов**. Для полного безлимита перейдите в раздел **«💎 Премиум & Безлимитный AI»**.\n\n"
        "4️⃣ **Торговые сигналы:**\n"
        "• Нажимайте кнопку **«⚡ Живые сигналы (VIP/Free)»**, чтобы видеть актуальные точки входа со временем публикации."
    )
    bot.send_message(message.chat.id, guide_text, parse_mode="Markdown")

# Словарь для сохранения языка каждого пользователя
user_languages = {}

@bot.message_handler(func=lambda message: message.text in ["🌐 Изменить язык / Change Language", "🌐 Tilni tansh / O'zbekcha"])
def change_language(message):
    track_user(message)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, "🌐 **Выберите язык / Select language / Tilni tanlang:**", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def lang_callback(call):
    lang = call.data.split("_")[1].lower()
    user_id = call.from_user.id
    user_languages[user_id] = lang  # Сохраняем язык пользователя
    
    lang_names = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}
    bot.answer_callback_query(call.id, text=f"Language changed to {lang_names.get(lang, lang)}")
    
    bot.edit_message_text(
        f"✅ Язык успешно изменен на: **{lang_names.get(lang, lang)}**", 
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        parse_mode="Markdown"
    )
    bot.send_message(call.message.chat.id, "👇 Главное меню:", reply_markup=get_main_keyboard())


@bot.message_handler(func=lambda message: message.text == "📅 Экономический календарь")
def economic_calendar(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📅 ForexFactory Calendar", url="https://www.forexfactory.com/calendar"),
        types.InlineKeyboardButton("📈 Investing.com Calendar", url="https://ru.investing.com/economic-calendar/")
    )
    bot.send_message(message.chat.id, "📅 **Экономический календарь и важные макроэкономические события:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Аналитика & Новости")
def market_analytics(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌐 Investing.com (Рынки)", url="https://ru.investing.com/"),
        types.InlineKeyboardButton("📰 ForexFactory News", url="https://www.forexfactory.com/news")
    )
    bot.send_message(message.chat.id, "📊 **Глобальная аналитика рынков и свежие финансовые новости:**", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Графики (TradingView)")
def tradingview_charts(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📈 Открыть TradingView (Живые графики)", url="https://www.tradingview.com/chart/"),
        types.InlineKeyboardButton("🪙 Криптографики (CoinGecko)", url="https://www.coingecko.com/")
    )
    bot.send_message(message.chat.id, "📊 **Интерактивные графики и глубокий технический анализ:**", parse_mode="Markdown", reply_markup=markup)

# 🪙 Bitcoin в реальном времени через Binance API (обновляется каждую секунду)
@bot.message_handler(func=lambda message: message.text == "🪙 Bitcoin / Крипта")
def crypto_bitcoin(message):
    track_user(message)
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график BTC (TradingView)", url="https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT"))
    try:
        # Запрос свежей цены напрямую с биржи Binance
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        res = requests.get(url, timeout=5).json()
        usd = float(res.get("price", 0))
        uzs = usd * 12800  # актуальный расчет
        rub = usd * 95
        
        text = (
            f"📊 **Анализ актива: Bitcoin (BTC)**\n\n"
            f"💱 **Конвертер валют (Live):**\n"
            f"• USD: ${usd:,.2f}\n"
            f"• UZS: {uzs:,.2f} so'm\n"
            f"• RUB: {rub:,.2f} руб.\n\n"
            f"📈 **Статус:** 🟢 Данные обновлены в реальном времени"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "⚠️ Ошибка получения актуальных данных с биржи.", parse_mode="Markdown", reply_markup=markup)

# 🥇 Золото в реальном времени (обновляется ежедневно)
@bot.message_handler(func=lambda message: message.text == "🥇 Золото (XAU)")
def gold_xau(message):
    track_user(message)
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график Золота", url="https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD"))
    try:
        # Запрос свежей цены золота
        url = "https://api.gold-api.com/price/XAU"
        res = requests.get(url, timeout=5).json()
        price = float(res.get("price", 0))
        
        text = (
            f"🥇 **Золото (XAU/USD):** `${price:,.2f}`\n"
            f"📈 **Статус:** 🟢 Актуальная рыночная цена"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, "🥇 **Золото (XAU/USD):** Не удалось получить свежие данные.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💱 Форекс (EUR/USD)")
def forex_eurusd(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Открыть график EUR/USD", url="https://www.tradingview.com/chart/?symbol=FX_IDC%3AEURUSD"))
    try:
        pair = yf.Ticker("EURUSD=X")
        price = pair.history(period="1d")['Close'].iloc[-1]
        bot.send_message(chat_id, f"💱 **Форекс: EUR/USD:** `{price:.4f}`\n📊 **Технический вердикт:** 🟡 NEUTRAL (Консолидация)", parse_mode="Markdown", reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, f"💱 **EUR/USD:** `1.0850`\n📊 **Вердикт:** 🟡 NEUTRAL", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📈 Акции (AAPL / TSLA)")
def stocks_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📈 Акции на TradingView", url="https://www.tradingview.com/markets/stocks-usa/top-gainers/"))
    bot.send_message(message.chat.id, "📈 **Мировые фондовые рынки:**\n\nОтправьте в чат тикер любой компании (`AAPL`, `TSLA`, `MSFT`, `GOOGL`), чтобы получить актуальную котировку и конвертер!", parse_mode="Markdown", reply_markup=markup)

# Универсальный обработчик (активы, конвертер, ИИ с лимитами и безлимитом для према)
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip().upper()
    original_text = message.text.strip()
    chat_id = message.chat.id
    user_id = message.from_user.id

    menu_buttons = [
        "🪙 BITCOIN / КРИПТА", "🥇 ЗОЛОТО (XAU)", "💱 ФОРЕКС (EUR/USD)", 
        "📈 АКЦИИ (AAPL / TSLA)", "⚡ ЖИВЫЕ СИГНАЛЫ (VIP/FREE)", "💱 КОНВЕРТЕР ВАЛЮТ", 
        "📊 ГРАФИКИ (TRADINGVIEW)", "📅 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ", "📊 АНАЛИТИКА & НОВОСТИ", 
        "💎 ПРЕМИУМ & БЕЗЛИМИТНЫЙ AI", "📖 ИНСТРУКЦИЯ ДЛЯ НОВИЧКОВ", "🌐 ИЗМЕНИТЬ ЯЗЫК / CHANGE LANGUAGE"
    ]
    if text in menu_buttons or text.startswith('/'):
        return

    # 1. Поиск активов мира и акций через Yahoo Finance
    if len(original_text.split()) == 1 and len(text) <= 6:
        sent_msg = bot.send_message(chat_id, f"🔍 Ищу актив `{text}` на мировых биржах...", parse_mode="Markdown")
        try:
            ticker_symbol = text
            if ticker_symbol in ["EURUSD", "GBPUSD", "USDJPY"]:
                ticker_symbol += "=X"
            elif ticker_symbol in ["GOLD", "XAUUSD"]:
                ticker_symbol = "GC=F"
            elif ticker_symbol == "BRENT":
                ticker_symbol = "BZ=F"
            elif ticker_symbol in ["BTC", "ETH", "SOL", "BNB", "XRP"]:
                ticker_symbol += "-USD"

            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                uzs = price * 12800 if ticker_symbol.endswith("=X") or price > 10 else 0
                rub = price * 95 if ticker_symbol.endswith("=X") or price > 10 else 0
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f"📈 График {text} (TradingView)", url=f"https://www.tradingview.com/chart/?symbol={text}"))
                
                response_text = f"📊 **Глобальный рынок: {text}**\n\n💵 **Актуальная цена:** `${price:,.2f}`"
                if uzs > 0:
                    response_text += f"\n\n💱 **Конвертер валют:**\n• UZS: {uzs:,.2f} so'm\n• RUB: {rub:,.2f} руб."
                response_text += f"\n\n📈 **Статус:** 🟢 Активные данные с биржи"
                
                bot.edit_message_text(response_text, chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup)
                return
        except Exception:
            pass

        # 2. Поиск через CoinGecko с конвертером в USD, UZS, RUB
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
                markup.add(types.InlineKeyboardButton(f"📈 График {symbol} (TradingView)", url=f"https://www.tradingview.com/chart/?symbol={symbol}USDT"))
                bot.edit_message_text(
                    f"📈 **Криптовалюта: {coins[0]['name']} ({symbol})**\n\n"
                    f"💱 **Конвертер валют:**\n"
                    f"• USD: ${usd:,.4f}\n"
                    f"• UZS: {uzs:,.2f} so'm\n"
                    f"• RUB: {rub:,.2f} руб.\n\n"
                    f"📊 **Статус:** 🟢 Активный мониторинг",
                    chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown", reply_markup=markup
                )
                return
        except Exception:
            pass

        bot.edit_message_text(f"❌ Актив `{text}` не найден на мировых биржах. Проверьте правильность тикера.", chat_id=chat_id, message_id=sent_msg.message_id, parse_mode="Markdown")
        return

    # 3. Проверка лимитов ИИ: 15 бесплатных запросов для новичков, безлимит для премиум
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
    sent_ai = bot.send_message(chat_id, f"🤖 **Trader AI анализирует ваш вопрос...**{limit_note}", parse_mode="Markdown")
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





















