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

# Твой ключ Gemini
GEMINI_API_KEY = ""

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

def get_trader_ai_response(prompt_text):
    if not GEMINI_API_KEY:
        return "🤖 **Trader AI (VIP):** Ключ активации не найден."
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"Ты профессиональный финансовый и крипто-аналитик Trader AI. Ответь кратко, четко и полезно на этот вопрос трейдера: {prompt_text}"}]
            }]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = response.json()
        answer = res_json['candidates'][0]['content']['parts'][0]['text']
        return f"🤖 **Trader AI (VIP Аналитик):**\n\n{answer}"
    except Exception as e:
        return "⚠️ Trader AI обрабатывает слишком много запросов. Попробуйте еще раз через пару секунд."

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
        'welcome': "👋 **Assalomu aleykum! Global Spot & Trading Terminaliga xush kelibsiz.**\n\nSizda **15 ta bepul urinish** mavjud. Pastdagi menyudan foydalaning:",
        'btn_btc': "🪙 Bitcoin narxi",
        'btn_gold': "🥇 Oltin (XAU)",
        'btn_macro': "🌍 Makro Kalendar (NFP)",
        'btn_sentiment': "🌡 Bozor Kayfiyati",
        'btn_premium': "💎 Premium & Trader AI",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'macro_info': "🌍 **Global Makro Kalendar:** NFP, CPI va FRS stavkalari bozorga ta'siri.",
        'premium_info': "💎 **Premium Trader & Trader AI**\n\n🚀 Cheksiz tahlillar, Trader AI maslahatchisi va smart-signallar!\n👇 100 Telegram Stars evaziga cheksiz huquqni oling:",
        'buy_premium': "⭐ Premium sotib olish (100 Stars)",
        'limit_exceeded': "⚠️ **Bepul urinishlar tugadi!**\n\nBarcha cheklovlarni olib tashlash va Trader AI bilan cheksiz muloqot qilish uchun **Premium** sotib oling:",
        'not_found': "❌ Aktiv topilmadi. Masalan: `bitcoin`, `solana`, `gold`.",
        'error': "⚠️ Xatolik yuz berdi.",
    },
    'ru': {
        'welcome': "👋 **Добро пожаловать в глобальный трейдинг-терминал.**\n\nВам доступно **15 бесплатных запросов**. Используйте меню внизу:",
        'btn_btc': "🪙 Цена Bitcoin",
        'btn_gold': "🥇 Золото (XAU)",
        'btn_macro': "🌍 Макро Календарь (NFP)",
        'btn_sentiment': "🌡 Настроение рынка",
        'btn_premium': "💎 Премиум & Trader AI",
        'btn_lang': "🌐 Изменить язык",
        'macro_info': "🌍 **Глобальный макрокалендарь:** Аналитика NFP, инфляции и ставок ФРС.",
        'premium_info': "💎 **Премиум-доступ & Trader AI**\n\n🚀 Безлимитные запросы, персональный анализ от Trader AI и VIP-сигналы!\n👇 Активируйте безлимит за 100 Telegram Stars:",
        'buy_premium': "⭐ Купить Премиум (100 Stars)",
        'limit_exceeded': "⚠️ **Бесплатные попытки исчерпаны!**\n\nЧтобы снять все лимиты и общаться с продвинутым Trader AI, оформите **Премиум**:",
        'not_found': "❌ Актив не найден. Проверьте запрос (`bitcoin`, `ethereum`, `gold`).",
        'error': "⚠️ Ошибка обработки.",
    },
    'en': {
        'welcome': "👋 **Welcome to Global Trading Terminal.**\n\nYou have **15 free requests**. Use the menu below:",
        'btn_btc': "🪙 Bitcoin Price",
        'btn_gold': "🥇 Gold (XAU)",
        'btn_macro': "🌍 Macro Calendar (NFP)",
        'btn_sentiment': "🌡 Market Sentiment",
        'btn_premium': "💎 Premium & Trader AI",
        'btn_lang': "🌐 Change Language",
        'macro_info': "🌍 **Global Macro Calendar:** NFP, CPI and Fed rate impacts.",
        'premium_info': "💎 **Premium Trader & Trader AI**\n\n🚀 Unlimited analysis, Trader AI assistant and smart signals!\n👇 Get unlimited access for 100 Telegram Stars:",
        'buy_premium': "⭐ Buy Premium (100 Stars)",
        'limit_exceeded': "⚠️ **Free requests exhausted!**\n\nTo remove all limits and chat with Trader AI, get **Premium**:",
        'not_found': "❌ Asset not found. Example: `bitcoin`, `solana`, `gold`.",
        'error': "⚠️ An error occurred.",
    },
    'tr': {
        'welcome': "👋 **Küresel İşlem Terminaline Hoş Geldiniz.**\n\n**15 ücretsiz hakkınız** var. Aşağıdaki menüyü kullanın:",
        'btn_btc': "🪙 Bitcoin Fiyatı",
        'btn_gold': "🥇 Altın (XAU)",
        'btn_macro': "🌍 Makro Takvim (NFP)",
        'btn_sentiment': "🌡 Piyasa Duygu Durumu",
        'btn_premium': "💎 Premium & Trader AI",
        'btn_lang': "🌐 Dili Değiştir",
        'macro_info': "🌍 **Küresel Makro Takvim:** NFP, TÜFE ve Fed faiz kararlarının piyasaya etkisi.",
        'premium_info': "💎 **Premium Trader & Trader AI**\n\n🚀 Sınırsız analiz, Trader AI asistanı ve akıllı sinyaller!\n👇 100 Telegram Stars karşılığında edinin:",
        'buy_premium': "⭐ Premium Satın Al (100 Stars)",
        'limit_exceeded': "⚠️ **Ücretsiz haklarınız bitti!**\n\nTüm sınırları kaldırmak ve Trader AI ile sohbet etmek için **Premium** alın:",
        'not_found': "❌ Varlık bulunamadı. Örnek: `bitcoin`, `solana`, `gold`.",
        'error': "⚠️ Bir hata oluştu.",
    }
}

def get_main_keyboard(lang='uz'):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    t = LANGUAGES.get(lang, LANGUAGES['uz'])
    kb.add(
        types.KeyboardButton(t['btn_btc']),
        types.KeyboardButton(t['btn_gold']),
        types.KeyboardButton(t['btn_macro']),
        types.KeyboardButton(t['btn_sentiment']),
        types.KeyboardButton(t['btn_premium']),
        types.KeyboardButton(t['btn_lang'])
    )
    return kb

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    bot.send_message(chat_id, "🌍 **Global Spot & Trading Terminal**\n\nSelect language / Tilni tanlang / Выберите язык / Dil seçin:", reply_markup=markup, parse_mode="Markdown")

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

    if text in ["🌐 Изменить язык", "🌐 Tilni o'zgartirish", "🌐 Change Language", "🌐 Dili Değiştir"]:
        send_welcome(message)
        return

    if text in ["💎 Премиум & Trader AI", "💎 Premium & Trader AI"]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t['buy_premium'], callback_data="buy_premium_stars"))
        bot.send_message(chat_id, t['premium_info'], reply_markup=markup, parse_mode="Markdown")
        return

    if chat_id not in premium_users:
        used = user_requests_count.get(chat_id, 0)
        if used >= FREE_LIMIT:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['buy_premium'], callback_data="buy_premium_stars"))
            bot.send_message(chat_id, t['limit_exceeded'], reply_markup=markup, parse_mode="Markdown")
            return
        else:
            user_requests_count[chat_id] = used + 1

    if text in ["🌍 Макро Календарь (NFP)", "🌍 Makro Kalendar (NFP)", "🌍 Macro Calendar (NFP)", "🌍 Makro Takvim (NFP)"]:
        bot.send_message(chat_id, t['macro_info'], parse_mode="Markdown")
        return

    if text in ["🌡 Настроение рынка", "🌡 Bozor Kayfiyati", "🌡 Market Sentiment", "🌡 Piyasa Duygu Durumu"]:
        val, label = get_fear_and_greed()
        res_text = (
            f"🌡 **Индекс Страха и Жадности (Crypto Sentiment)**\n\n"
            f"• **Значение:** `{val}/100`\n"
            f"• **Фаза рынка:** `✨ {label} ✨`"
        )
        bot.send_message(chat_id, res_text, parse_mode="Markdown")
        return

    if text in ["🪙 Цена Bitcoin", "🪙 Bitcoin narxi", "🪙 Bitcoin Price", "🪙 Bitcoin Fiyatı"]:
        res = analyze_market_asset("bitcoin")
        if res:
            p = res['prices']
            res_text = (
                f"🪙 **Bitcoin (BTC) - Спот-анализ**\n\n"
                f"💰 **Цена:**\n"
                f"• USD: `${p.get('usd', 0):,.2f}`\n"
                f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
                f"• RUB: `{p.get('rub', 0):,.2f} руб.`\n\n"
                f"📈 **Тренд:** {res['tech_verdict']} (`{res['change_24h']:+.2f}%`)"
            )
            bot.send_message(chat_id, res_text, parse_mode="Markdown")
        return

    if text in ["🥇 Золото (XAU)", "🥇 Oltin (XAU)", "🥇 Gold (XAU)", "🥇 Altın (XAU)"]:
        price = get_gold_price()
        res_text = (
            f"🥇 **Золото (XAU/USD) - Глобальный Спот**\n\n"
            f"💰 **Котировки:**\n"
            f"• USD: `${price:,.2f}` (troy oz)\n"
            f"• UZS: `${price * 12800:,.2f} so'm`\n"
            f"• RUB: `${price * 95:,.2f} руб.`"
        )
        bot.send_message(chat_id, res_text, parse_mode="Markdown")
        return

    try:
        bot.send_chat_action(chat_id, 'typing')
        
        if chat_id in premium_users:
            res_text = get_trader_ai_response(text)
        else:
            res = analyze_market_asset(text)
            if res:
                p = res['prices']
                res_text = (
                    f"🤖 **Сигнал & Анализ: {res['name']} ({res['symbol']})**\n\n"
                    f"💰 **Цена:**\n"
                    f"• USD: `${p.get('usd', 0):,.4f}`\n"
                    f"• UZS: `${p.get('uzs', 0):,.2f} so'm`\n"
                    f"• RUB: `${p.get('rub', 0):,.4f} руб.`\n\n"
                    f"📈 **Вердикт:** {res['tech_verdict']}\n"
                    f"📊 **Осталось бесплатных попыток:** `{max(0, FREE_LIMIT - user_requests_count.get(chat_id, 0))}`"
                )
            else:
                res_text = t['not_found']
    except:
        res_text = t['error']

    bot.send_message(chat_id, res_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium_stars")
def buy_premium(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⚡ Генерация счета...")
    try:
        bot.send_invoice(
            chat_id=chat_id,
            title="CryptoScan VIP & Trader AI",
            description="Безлимитный доступ к рынку и персональному аналитику Trader AI.",
            invoice_payload="premium_sub",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="VIP Trader AI", amount=100)]
        )
    except:
        bot.send_message(chat_id, "✨ Свяжитесь с поддержкой для активации.")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    premium_users.add(chat_id)
    bot.send_message(chat_id, "🎉 Оплата прошла успешно! Вам активирован **безлимитный доступ и персональный Trader AI**.")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    return "Spot Bot is running on Render!", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://spot-bot-new.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
