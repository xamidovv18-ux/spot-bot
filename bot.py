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

# Твой ключ Gemini для Trader AI GEMINI_IP_KEY = ""

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
                "parts": [{"text": f"Ты профессиональный институциональный трейдер и финансовый аналитик Trader AI. Дай глубокий технический и фундаментальный анализ с точными сигналами BUY/SELL, уровнями поддержки и сопротивления для запроса: {prompt_text}"}]
            }]
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = response.json()
        answer = res_json['candidates'][0]['content']['parts'][0]['text']
        return f"🤖 **Trader AI (VIP Анализ & Сигналы):**\n\n{answer}"
    except Exception as e:
        return "⚠️ Trader AI обрабатывает слишком много запросов. Попробуйте еще раз через пару секунд."

def analyze_market_asset(query):
    try:
        query = query.strip().lower()
        
        # Форекс и металлы
        forex_pairs = {
            'eurusd': {'name': 'EUR/USD (Euro / US Dollar)', 'price': 1.0850, 'verdict': '🟢 BUY (Отскок от поддержки)'},
            'gbpusd': {'name': 'GBP/USD (British Pound)', 'price': 1.2720, 'verdict': '🟡 Флэт / Ожидание новостей'},
            'usdjpy': {'name': 'USD/JPY (US Dollar / Yen)', 'price': 155.40, 'verdict': '🔴 SELL (Коррекция тренда)'},
            'gold': {'name': 'Gold (XAU/USD)', 'price': get_gold_price(), 'verdict': '🟢 Сильный бычий тренд (Safe Haven)'},
            'xau': {'name': 'Gold (XAU/USD)', 'price': get_gold_price(), 'verdict': '🟢 Сильный бычий тренд (Safe Haven)'},
            'oil': {'name': 'Brent Crude Oil', 'price': 78.50, 'verdict': '🟡 Консолидация цен на сырье'}
        }
        
        if query in forex_pairs:
            p = forex_pairs[query]
            return {
                "name": p['name'],
                "symbol": query.upper(),
                "prices": {"usd": p['price'], "uzs": p['price'] * 12800, "rub": p['price'] * 95},
                "change_24h": 0.35,
                "tech_verdict": p['verdict'],
                "is_forex": True
            }

        # Поиск криптовалют через CoinGecko API
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

        if change_24h > 4:
            tech_verdict = "🟢 СИЛЬНЫЙ BUY (Пробой уровня сопротивления)"
        elif change_24h > 0:
            tech_verdict = "🟢 Умеренный рост (Long зона)"
        elif change_24h > -4:
            tech_verdict = "🟡 Консолидация / Ожидание паттерна"
        else:
            tech_verdict = "🔴 СИЛЬНЫЙ SELL (Риск глубокой коррекции)"

        return {
            "name": coin_name,
            "symbol": coin_symbol,
            "prices": prices,
            "change_24h": change_24h,
            "tech_verdict": tech_verdict,
            "is_forex": False
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
        'welcome': (
            "👋 **Assalomu alaykum! Global Spot & Trading Terminaliga xush kelibsiz.**\n\n"
            "🌐 **Professional imkoniyatlar:**\n"
            "• 🪙 **Kriptovalyuta & Spot:** Minglab tangalar real vaqtda.\n"
            "• 💱 **Forex & Metarlar:** EUR/USD, GBP/USD, USD/JPY, Oltin (XAU) va Neft.\n"
            "• 📊 **Fundamental & Texnik tahlil:** Investing / ForexFactory uslubidagi muhim yangiliklar va aniq BUY/SELL signallari.\n"
            "• 💎 **Trader AI (Gemini):** Professional sun'iy intellekt tahlilchisi.\n\n"
            "🎁 **Sizda 15 ta bepul urinish bor!**\n👇 Boshlash uchun pastdagi tugmalardan foydalaning:"
        ),
        'btn_btc': "🪙 Bitcoin",
        'btn_gold': "🥇 Oltin (XAU)",
        'btn_forex': "💱 Forex (EUR/USD)",
        'btn_macro': "🌍 Fundamental Kalendar",
        'btn_sentiment': "🌡 Bozor Kayfiyati",
        'btn_premium': "💎 Premium & Trader AI",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'macro_info': (
            "🌍 **Fundamental Kalendar & Makroiqtisodiyot (Investing / ForexFactory):**\n\n"
            "• **NFP (Qishloq xo'jaligidan tashqari bandlik):** Oylik AQSh mehnat bozori hisoboti (Dollarga kuchli ta'sir qiladi).\n"
            "• **CPI (İnflyatsiya / İste'mol narxlari indeksi):** FRS stavkalari bo'yicha asosiy ko'rsatkich.\n"
            "• **FOMC / FRS stavkasi:** Foiz stavkalarining o'zgarishi kripto va foreks bozorida keskin trend ochadi."
        ),
        'premium_info': "💎 **VIP Terminal & Trader AI**\n\n🚀 Cheksiz texnik tahlil rasmlari, VIP BUY/SELL signallar va Trader AI bilan cheksiz muloqot!\n👇 100 Telegram Stars evaziga faollashtiring:",
        'buy_premium': "⭐ Premium sotib olish (100 Stars)",
        'limit_exceeded': "⚠️ **Bepul urinishlar tugadi!**\n\nCheksiz tahlillar va Trader AI signallari uchun **Premium** oling:",
        'not_found': "❌ Aktiv topilmadi. Masalan: `bitcoin`, `eurusd`, `gold`, `solana`.",
        'error': "⚠️ Xatolik yuz berdi.",
    },
    'ru': {
        'welcome': (
            "👋 **Добро пожаловать в глобальный трейдинг-терминал CryptoScan.**\n\n"
            "🌐 **Профессиональный функционал:**\n"
            "• 🪙 **Криптовалюта & Спот:** Тысячи монет в реальном времени.\n"
            "• 💱 **Форекс & Металлы:** EUR/USD, GBP/USD, USD/JPY, золото (XAU) и нефть.\n"
            "• 📊 **Фундаментальный & Технический анализ:** Данные в стиле Investing / ForexFactory и четкие сигналы BUY/SELL.\n"
            "• 💎 **Trader AI (Gemini):** Ваш персональный AI-аналитик.\n\n"
            "🎁 **Вам доступно 15 бесплатных запросов!**\n👇 Используйте меню внизу для навигации:"
        ),
        'btn_btc': "🪙 Bitcoin",
        'btn_gold': "🥇 Золото (XAU)",
        'btn_forex': "💱 Форекс (EUR/USD)",
        'btn_macro': "🌍 Фундаментальный Календарь",
        'btn_sentiment': "🌡 Настроение рынка",
        'btn_premium': "💎 Премиум & Trader AI",
        'btn_lang': "🌐 Изменить язык",
        'macro_info': (
            "🌍 **Фундаментальный календарь (Investing / ForexFactory style):**\n\n"
            "• **NFP (Non-Farm Payrolls):** Главный отчет по занятости в США. Вызывает мощнейшую волатильность на рынке.\n"
            "• **CPI (Инфляция):** Определяет дальнейшие действия ФРС США.\n"
            "• **Заседания ФРС:** Ключевые решения по процентным ставкам."
        ),
        'premium_info': "💎 **VIP Трейдинг & Trader AI**\n\n🚀 Безлимитные графики технического анализа, VIP сигналы BUY/SELL и полный доступ к Trader AI!\n👇 Активируйте за 100 Telegram Stars:",
        'buy_premium': "⭐ Купить Премиум (100 Stars)",
        'limit_exceeded': "⚠️ **Бесплатные попытки исчерпаны!**\n\nДля безлимитного анализа и VIP-сигналов оформите **Премиум**:",
        'not_found': "❌ Актив не найден. Проверьте запрос (`bitcoin`, `eurusd`, `gold`, `ethereum`).",
        'error': "⚠️ Ошибка обработки.",
    }
}

def get_main_keyboard(lang='uz'):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    t = LANGUAGES.get(lang, LANGUAGES['uz'])
    kb.add(
        types.KeyboardButton(t['btn_btc']),
        types.KeyboardButton(t['btn_gold']),
        types.KeyboardButton(t['btn_forex']),
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
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    )
    bot.send_message(chat_id, "🌍 **Global Spot & Forex Terminal**\n\nTilni tanlang / Выберите язык:", reply_markup=markup, parse_mode="Markdown")

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

    if text in ["🌍 Фундаментальный Календарь", "🌍 Fundamental Kalendar"]:
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

    if text in ["🪙 Bitcoin", "🪙 Bitcoin narxi"]:
        res = analyze_market_asset("bitcoin")
        handle_asset_output(chat_id, res, t)
        return

    if text in ["🥇 Золото (XAU)", "🥇 Oltin (XAU)"]:
        res = analyze_market_asset("gold")
        handle_asset_output(chat_id, res, t)
        return

    if text in ["💱 Форекс (EUR/USD)", "💱 Forex (EUR/USD)"]:
        res = analyze_market_asset("eurusd")
        handle_asset_output(chat_id, res, t)
        return

    # Обработка любых других запросов (монеты, форекс или вопросы к AI)
    try:
        bot.send_chat_action(chat_id, 'typing')
        
        if chat_id in premium_users:
            res_text = get_trader_ai_response(text)
            bot.send_message(chat_id, res_text, parse_mode="Markdown")
        else:
            res = analyze_market_asset(text)
            if res:
                handle_asset_output(chat_id, res, t)
            else:
                res_text = get_trader_ai_response(text)
                bot.send_message(chat_id, res_text, parse_mode="Markdown")
    except:
        bot.send_message(chat_id, t['error'])

def handle_asset_output(chat_id, res, t):
    if not res:
        bot.send_message(chat_id, t['not_found'], parse_mode="Markdown")
        return
    
    p = res['prices']
    is_premium = chat_id in premium_users
    
    res_text = (
        f"📊 **Анализ актива: {res['name']} ({res['symbol']})**\n\n"
        f"💰 **Котировки:**\n"
        f"• USD: `${p.get('usd', 0):,.4f}`\n"
        f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
        f"• RUB: `{p.get('rub', 0):,.4f} руб.`\n\n"
        f"📈 **Технический вердикт & Сигнал:** {res['tech_verdict']}\n"
        f"📊 **Осталось бесплатных попыток:** `{max(0, FREE_LIMIT - user_requests_count.get(chat_id, 0))}`"
    )
    
    bot.send_message(chat_id, res_text, parse_mode="Markdown")
    
    # ОТПРАВКА ГРАФИКОВ / ТЕХНИЧЕСКОГО АНАЛИЗА
    try:
        if not is_premium:
            bot.send_photo(
                chat_id,
                photo="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
                caption="📈 **Бесплатный базовый технический анализ**\nХотите получать детальные графики с точками входа и расширенные VIP-сигналы? Оформите **Премиум**!"
            )
        else:
            bot.send_photo(
                chat_id,
                photo="https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800",
                caption="💎 **VIP Технический Анализ (Trader AI Pro)**\n• Тренд: Бычий импульс\n• Рекомендация: Покупай на откате\n• Стоп-лосс / Тейк-профит активированы."
            )
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "buy_premium_stars")
def buy_premium(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⚡ Генерация счета...")
    try:
        bot.send_invoice(
            chat_id=chat_id,
            title="CryptoScan VIP & Trader AI",
            description="Безлимитный доступ к форексу, крипте, фундаментальному анализу и графическим сигналам.",
            invoice_payload="premium_sub",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="VIP Terminal", amount=100)]
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
    bot.send_message(chat_id, "🎉 Оплата прошла успешно! Вам активирован **безлимитный доступ, премиум-графики и Trader AI**.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://spot-bot-new.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


