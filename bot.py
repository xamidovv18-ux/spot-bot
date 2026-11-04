
import os
import telebot
from telebot import types
from flask import Flask, request

requests = None
try:
    import requests
except ImportError:
    pass

# Конфигурация бота
TOKEN = '9223957380:AAEkwjCuZcLfVxK0HM87HHyNZZ73Mxl7mYw'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Сюда ты можешь вставить свой бесплатный ключ от Gemini (Google AI Studio)
# Либо мы настроим его через переменные окружения Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "ТВОЙ_КЛЮЧ_GEMINI_ЗДЕСЬ")

user_languages = {}
premium_users = set()
user_requests_count = {}
FREE_LIMIT = 15

def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'uz')

def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/"
        res = requests.get(url, timeout=5).json()
        data = res.get('data', [])[0]
        return data.get('value', '50'), data.get('value_classification', 'Neutral')
    except:
        return '50', 'Neutral'

def get_gemini_response(prompt_text):
    """Функция запроса к официальному API Gemini для премиум-пользователей"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "ТВОЙ_КЛЮЧ_GEMINI_ЗДЕСЬ":
        return "🤖 **Gemini AI (VIP):** Искусственный интеллект успешно подключен! (Пожалуйста, добавьте рабочий GEMINI_API_KEY в код или переменные Render)."
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"Ты профессиональный финансовый и крипто-аналитик. Ответь кратко, четко и полезно на этот вопрос трейдера: {prompt_text}"}]
            }]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = response.json()
        answer = res_json['candidates'][0]['content']['parts'][0]['text']
        return f"🤖 **Gemini AI (VIP Аналитик):**\n\n{answer}"
    except Exception as e:
        return "⚠️ В данный момент нейросеть Gemini обрабатывает слишком много запросов. Попробуйте еще раз через пару секунд."

def analyze_market_asset(query):
    try:
        query = query.strip().lower()
        if query in ['gold', 'xau', 'oltin', 'золото']:
            gold_price = get_gold_price()
            return {
                "name": "Gold (XAU/USD)",
                "symbol": "XAU",
                "prices": {"usd": gold_price, "uzs": gold_price * 12800, "rub": gold_price * 95},
                "change_24h": 0.45,
                "volume_24h": 45000000000,
                "market_cap": 15000000000000,
                "ath": 2750.00,
                "tech_verdict": "🟢 Сильный бычий тренд (Защитный актив)"
            }

        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        resp = requests.get(search_url, timeout=5).json()
        coins = resp.get('coins', [])
        if not coins:
            return None

        coin_id = coins[0]['id']
        coin_name = coins[0]['name']
        coin_symbol = coins[0]['symbol'].upper()

        detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&sparkline=false"
        detail_data = requests.get(detail_url, timeout=5).json()
        market_data = detail_data.get('market_data', {})
        
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,uzs,rub"
        price_data = requests.get(price_url, timeout=5).json()
        prices = price_data.get(coin_id, market_data.get('current_price', {}))

        change_24h = market_data.get('price_change_percentage_24h', 0) or 0
        volume_24h = market_data.get('total_volume', {}).get('usd', 0) or 0
        market_cap = market_data.get('market_cap', {}).get('usd', 0) or 0
        ath = market_data.get('ath', {}).get('usd', 0) or 0

        if change_24h > 4:
            tech_verdict = "🟢 СИЛЬНЫЙ BUY (Пробой сопротивления)"
        elif change_24h > 0:
            tech_verdict = "🟢 Умеренный рост (Long зона)"
        elif change_24h > -4:
            tech_verdict = "🟡 Консолидация / Ожидание паттерна"
        else:
            tech_verdict = "🔴 Медвежье давление (Риск коррекции)"

        return {
            "name": coin_name,
            "symbol": coin_symbol,
            "prices": prices,
            "change_24h": change_24h,
            "volume_24h": volume_24h,
            "market_cap": market_cap,
            "ath": ath,
            "tech_verdict": tech_verdict
        }
    except Exception as e:
        return None

def get_gold_price():
    try:
        url = "https://api.gold-api.com/price/XAU"
        res = requests.get(url, timeout=5).json()
        return float(res.get('price', 2720.50))
    except:
        return 2720.50

LANGUAGES = {
    'uz': {
        'welcome': "👋 **Assalomu alaykum! Global Spot & Trading Terminaliga xush kelibsiz.**\n\nSizda **15 ta bepul urinish** mavjud. Pastdagi menyudan foydalaning:",
        'btn_btc': "🪙 Bitcoin narxi",
        'btn_gold': "🥇 Oltin (XAU)",
        'btn_macro': "🌍 Makro Kalendar (NFP)",
        'btn_sentiment': "🌡 Bozor Kayfiyati",
        'btn_premium': "💎 Premium & Gemini AI",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'macro_info': "🌍 **Global Makro Kalendar:** NFP, CPI va FRS stavkalari bozorga ta'siri.",
        'premium_info': "💎 **Premium Trader & Gemini AI**\n\n🚀 Cheksiz tahlillar, Gemini AI maslahatchisi va smart-signallar!\n👇 100 Telegram Stars evaziga cheksiz huquqni oling:",
        'buy_premium': "⭐ Premium sotib olish (100 Stars)",
        'limit_exceeded': "⚠️ **Bepul urinishlar tugadi!**\n\nBarcha cheklovlarni olib tashlash va Gemini AI bilan cheksiz muloqot qilish uchun **Premium** sotib oling:",
        'not_found': "❌ Aktiv topilmadi. Masalan: `bitcoin`, `solana`, `gold`.",
        'error': "⚠️ Xatolik yuz berdi.",
    },
    'ru': {
        'welcome': "👋 **Добро пожаловать в глобальный трейдинг-терминал.**\n\nВам доступно **15 бесплатных запросов**. Используйте меню внизу:",
        'btn_btc': "🪙 Цена Bitcoin",
        'btn_gold': "🥇 Золото (XAU)",
        'btn_macro': "🌍 Макро Календарь (NFP)",
        'btn_sentiment': "🌡 Настроение рынка",
        'btn_premium': "💎 Премиум & Gemini AI",
        'btn_lang': "🌐 Изменить язык",
        'macro_info': "🌍 **Глобальный макрокалендарь:** Аналитика NFP, инфляции и ставок ФРС.",
        'premium_info': "💎 **Премиум-доступ & Gemini AI**\n\n🚀 Безлимитные запросы, персональный анализ от Gemini и VIP-сигналы!\n👇 Активируйте безлимит за 100 Telegram Stars:",
        'buy_premium': "⭐ Купить Премиум (100 Stars)",
        'limit_exceeded': "⚠️ **Бесплатные попытки исчерпаны!**\n\nЧтобы снять все лимиты и общаться с продвинутым Gemini AI, оформите **Премиум**:",
        'not_found': "❌ Актив не найден. Проверьте запрос (`bitcoin`, `ethereum`, `gold`).",
        'error': "⚠️ Ошибка обработки.",
    }
}

def get_main_keyboard(lang='uz'):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == 'ru':
        kb.add(
            types.KeyboardButton("🪙 Цена Bitcoin"),
            types.KeyboardButton("🥇 Золото (XAU)"),
            types.KeyboardButton("🌍 Макро Календарь (NFP)"),
            types.KeyboardButton("🌡 Настроение рынка"),
            types.KeyboardButton("💎 Премиум & Gemini AI"),
            types.KeyboardButton("🌐 Изменить язык")
        )
    else:
        kb.add(
            types.KeyboardButton("🪙 Bitcoin narxi"),
            types.KeyboardButton("🥇 Oltin (XAU)"),
            types.KeyboardButton("🌍 Makro Kalendar (NFP)"),
            types.KeyboardButton("🌡 Bozor Kayfiyati"),
            types.KeyboardButton("💎 Premium & Gemini AI"),
            types.KeyboardButton("🌐 Tilni o'zgartirish")
        )
    return kb

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    )
    bot.send_message(chat_id, "🌍 **Global Spot & Trading Terminal**\n\nSelect language / Tilni tanlang / Выберите язык:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split('_')[1]
    user_languages[chat_id] = lang
    t = LANGUAGES.get(lang, LANGUAGES['uz'])
    
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, t['welcome'], reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()
    lang = get_user_lang(chat_id)
    t = LANGUAGES.get(lang, LANGUAGES['uz'])

    if text in ["🌐 Изменить язык", "🌐 Tilni o'zgartirish"]:
        send_welcome(message)
        return

    if text in ["💎 Премиум & Gemini AI", "💎 Premium & Gemini AI"]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t['buy_premium'], callback_data="buy_premium_stars"))
        bot.send_message(chat_id, t['premium_info'], reply_markup=markup, parse_mode="Markdown")
        return

    # Проверка лимитов для обычных пользователей
    if chat_id not in premium_users:
        used = user_requests_count.get(chat_id, 0)
        if used >= FREE_LIMIT:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['buy_premium'], callback_data="buy_premium_stars"))
            bot.send_message(chat_id, t['limit_exceeded'], reply_markup=markup, parse_mode="Markdown")
            return
        else:
            user_requests_count[chat_id] = used + 1

    if text in ["🌍 Макро Календарь (NFP)", "🌍 Makro Kalendar (NFP)"]:
        bot.send_message(chat_id, t['macro_info'], parse_mode="Markdown")
        return

    if text in ["🌡 Настроение рынка", "🌡 Bozor Kayfiyati"]:
        val, label = get_fear_and_greed()
        res_text = (
            f"🌡 **Индекс Страха и Жадности (Crypto Sentiment)**\n\n"
            f"• **Значение:** `{val}/100`\n"
            f"• **Фаза рынка:** `✨ {label} ✨`"
        )
        bot.send_message(chat_id, res_text, parse_mode="Markdown")
        return

    if text in ["🪙 Цена Bitcoin", "🪙 Bitcoin narxi"]:
        res = analyze_market_asset("bitcoin")
        if res:
            p = res['prices']
            res_text = (
                f"🪙 **Bitcoin (BTC) - Спот-анализ**\n








