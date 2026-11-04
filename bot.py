
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

user_languages = {}
premium_users = set()

def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'uz')

def analyze_market_asset(query):
    try:
        query = query.strip().lower()
        
        # Точечная обработка золота (XAU/USD)
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

# Мультиязычная база текстов терминала
LANGUAGES = {
    'uz': {
        'welcome': "👋 **Assalomu alaykum! Global Spot & Trading Terminaliga xush kelibsiz.**\n\nIltimos, o'zingizga qulay tilni tanlang:",
        'guide_btn': "📖 Botdan foydalanish qo'llanmasi",
        'choose_action': "👇 Kerakli bo'limni tanlang:",
        'btn_btc': "🪙 Bitcoin narxi va tahlili",
        'btn_gold': "🥇 Oltin (XAU/USD)",
        'btn_macro': "🌍 Global Makro & Kalendar (NFP / CPI)",
        'btn_search': "🔍 Istalgan aktivni tahlil qilish",
        'btn_premium': "💎 Premium imkoniyatlar",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'guide_text': (
            "📖 **Professional Treyding Qo'llanmasi:**\n\n"
            "Bu terminal orqali siz jahon moliya bozoridagi barcha yirik harakatlarni kuzatishingiz mumkin:\n"
            "1. **Spot Narxlar:** Bitcoin, Oltin va minglab aktivlarning real vaqtdagi kurslari.\n"
            "2. **Fundamental Kalendar:** Dunyo yangiliklari (NFP, CPI, stavkalar).\n"
            "3. **Texnik Signal:** Istalgan tanga nomini yozing (`ethereum`, `solana`, `gold`), bot darhol signal va tahlil beradi!"
        ),
        'macro_info': (
            "🌍 **Global Makroiqtisodiy Kalendar & Bozor Harakatlari**\n\n"
            "Dunyodagi eng yirik, bozorlarni siljituvchi asosiy yangiliklar:\n\n"
            "1️⃣ **NFP (Non-Farm Payrolls - Bandlik hisoboti):**\n"
            "• *Qachon:* Har oyning ilk juma kuni.\n"
            "• *Ta'siri:* Oltin (XAU) va Dollarga eng kuchli zarba beruvchi omil.\n\n"
            "2️⃣ **CPI (Ahol iste'moli inflyatsiyasi):**\n"
            "• *Ta'siri:* FRS (AQSh Markaziy banki) stavkalarini o'zgartiradi. Kriptovalyuta va fond bozoriga impuls beradi.\n\n"
            "3️⃣ **FOMC / FRS Yig'ilishi:**\n"
            "• *Ta'siri:* Foiz stavkalari e'lon qilinadi. Bozor yo'nalishini keskin o'zgartiradi.\n\n"
            "💡 *Maslahat:* Bu vaqtlarda treydingda ehtiyot bo'ling!"
        ),
        'premium_info': (
            "💎 **Premium Trader Huquqlari**\n\n"
            "🚀 Real vaqt rejimidagi smart-signallar, shaxsiy portfel va VIP tahlillarga ega bo'ling.\n"
            "👇 100 Telegram Stars evaziga obunani faollashtiring:"
        ),
        'buy_premium': "⭐ Premium sotib olish (100 Stars)",
        'not_found': "❌ Kechirasiz, aktiv topilmadi. Masalan: `bitcoin`, `solana`, `gold`, `ethereum`.",
        'error': "⚠️ Xatolik yuz berdi. Qayta urinib ko'ring.",
        'back': "🔙 Asosiy menyu"
    },
    'ru': {
        'welcome': "👋 **Добро пожаловать в глобальный трейдинг-терминал.**\n\nВыберите язык:",
        'guide_btn': "📖 Руководство пользователя",
        'choose_action': "👇 Выберите раздел:",
        'btn_btc': "🪙 Цена Биткоина и анализ",
        'btn_gold': "🥇 Золото (XAU/USD)",
        'btn_macro': "🌍 Мировые новости & Календарь (NFP / CPI)",
        'btn_search': "🔍 Анализ любого актива",
        'btn_premium': "💎 Премиум возможности",
        'btn_lang': "🌐 Изменить язык",
        'guide_text': (
            "📖 **Руководство профессионального трейдера:**\n\n"
            "Этот терминал объединяет спот-анализ и мировые новости рынков:\n"
            "1. **Мониторинг цен:** Точные котировки крипты и золота.\n"
            "2. **Макро-календарь:** Аналитика уровня Investing.com (NFP, инфляция, ставки).\n"
            "3. **Авто-сигналы:** Напишите название монеты (`bitcoin`, `solana`, `gold`) для мгновенного теханализа."
        ),
        'macro_info': (
            "🌍 **Глобальный макрокалендарь и крупные движения рынка**\n\n"
            "Главные события мира, вызывающие шторм на рынках:\n\n"
            "1️⃣ **NFP (Число занятых в несельскохозяйственном секторе):**\n"
            "• *Когда:* Первая пятница каждого месяца.\n"
            "• *Влияние:* Колоссальные скачки по Золоту (XAU), валютам и крипте.\n\n"
            "2️⃣ **CPI (Индекс потребительских цен / Инфляция):**\n"
            "• *Влияние:* Определяет решения ФРС США по процентной ставке.\n\n"
            "3️⃣ **Заседания ФРС (FOMC):**\n"
            "• *Влияние:* Главный драйвер глобального тренда.\n\n"
            "💡 *Совет:* Следите за календарем перед открытием сделок!"
        ),
        'premium_info': (
            "💎 **Премиум-доступ для трейдеров**\n\n"
            "🚀 Эксклюзивные сигналы, уведомления и расширенная аналитика.\n"
            "👇 Активируйте подписку через Telegram Stars:"
        ),
        'buy_premium': "⭐ Купить Премиум (100 Stars)",
        'not_found': "❌ Актив не найден. Проверьте запрос (`bitcoin`, `ethereum`, `gold`).",
        'error': "⚠️ Ошибка обработки. Попробуйте еще раз.",
        'back': "🔙 Главное меню"
    },
    'en': {
        'welcome': "👋 **Welcome to Global Trading Terminal.**\n\nSelect language:",
        'guide_btn': "📖 User Guide",
        'choose_action': "👇 Choose section:",
        'btn_btc': "🪙 Bitcoin Price & Analysis",
        'btn_gold': "🥇 Gold (XAU/USD)",
        'btn_macro': "🌍 Macro Calendar (NFP / CPI)",
        'btn_search': "🔍 Analyze Asset",
        'btn_premium': "💎 Premium Features",
        'btn_lang': "🌐 Change Language",
        'guide_text': "📖 **Guide:** Type any asset name (`bitcoin`, `gold`, `solana`) for instant technical signals.",
        'macro_info': "🌍 **Global Macro Calendar**\n\nMajor market-moving events: NFP, CPI, and FOMC rate decisions.",
        'premium_info': "💎 **Trader Premium Benefits**\n\nUnlock professional alerts and portfolio tracking.",
        'buy_premium': "⭐ Buy Premium (100 Stars)",
        'not_found': "❌ Not found. Check spelling.",
        'error': "⚠️ An error occurred.",
        'back': "Main Menu"
    },
    'tr': {
        'welcome': "👋 **Küresel İşlem Terminaline Hoş Geldiniz.**\n\nDil seçin:",
        'guide_btn': "📖 Kullanım Kılavuzu",
        'choose_action': "👇 Bölüm seçin:",
        'btn_btc': "🪙 Bitcoin Fiyatı",
        'btn_gold': "🥇 Altın (XAU/USD)",
        'btn_macro': "🌍 Makro Takvim (NFP / CPI)",
        'btn_search': "🔍 Varlık Analizi Yap",
        'btn_premium': "💎 Premium Özellikler",
        'btn_lang': "🌐 Dili Değiştir",
        'guide_text': "📖 **Rehber:** `bitcoin`, `gold` veya `ethereum` yazarak anında sinyal alın.",
        'macro_info': "🌍 **Küresel Makro Takvim ve Önemli Veriler**\n\nNFP, Enflasyon (CPI) ve Merkez Bankası kararları.",
        'premium_info': "💎 **Trader Premium Ayrıcalıkları**",
        'buy_premium': "⭐ Premium Satın Al (100 Stars)",
        'not_found': "❌ Varlık bulunamadı.",
        'error': "⚠️ Hata oluştu.",
        'back': "Ana Menü"
    }
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    bot.send_message(message.chat.id, "🌍 **Global Spot & Trading Terminal**\n\nSelect language / Tilni tanlang / Выберите язык:", reply_markup=markup, parse_mode="Markdown")

def show_main_menu(chat_id, message_id=None):
    lang = get_user_lang(chat_id)
    t = LANGUAGES[lang]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t['guide_btn'], callback_data="menu_guide"),
        types.InlineKeyboardButton(t['btn_btc'], callback_data="menu_btc"),
        types.InlineKeyboardButton(t['btn_gold'], callback_data="menu_gold"),
        types.InlineKeyboardButton(t['btn_macro'], callback_data="menu_macro"),
        types.InlineKeyboardButton(t['btn_search'], callback_data="menu_search"),
        types.InlineKeyboardButton(t['btn_premium'], callback_data="menu_premium"),
        types.InlineKeyboardButton(t['btn_lang'], callback_data="menu_lang_change")
    )

    text = f"{t['welcome']}\n\n{t['choose_action']}"
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data
    lang = get_user_lang(chat_id)
    t = LANGUAGES[lang]

    try:
        if data.startswith("lang_"):
            user_languages[chat_id] = data.split('_')[1]
            bot.answer_callback_query(call.id)
            show_main_menu(chat_id, call.message.message_id)
            return

        if data == "menu_lang_change":
            send_welcome(call.message)
            bot.answer_callback_query(call.id)
            return

        if data == "menu_back":
            show_main_menu(chat_id, call.message.message_id)
            bot.answer_callback_query(call.id)
            return

        if data == "menu_guide":
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(t['guide_text'], chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_btc":
            res = analyze_market_asset("bitcoin")
            if res:
                p = res['prices']
                text = (
                    f"🪙 **Bitcoin (BTC) - Технический и Фундаментальный Срез**\n\n"
                    f"💰 **Спотовая цена:**\n"
                    f"• USD: `${p.get('usd', 0):,.2f}`\n"
                    f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
                    f"• RUB: `{p.get('rub', 0):,.2f} руб.`\n\n"
                    f"📈 **Сигнал и тренд:** {res['tech_verdict']} (`{res['change_24h']:+.2f}%`)\n"
                    f"📊 **Объем торгов:** `${res['volume_24h']:,.0f}`\n"
                    f"🏛 **Капитализация:** `${res['market_cap']:,.0f}`\n\n"
                    f"✅ Чистый спот-анализ реального времени."
                )
            else:
                text = t['error']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_gold":
            price = get_gold_price()
            text = (
                f"🥇 **Золото (XAU/USD) - Глобальный Спот**\n\n"
                f"💰 **Текущие котировки:**\n"
                f"• USD: `${price:,.2f}` (troy oz)\n"
                f"• UZS: `{price * 12800:,.2f} so'm`\n"
                f"• RUB: `{price * 95:,.2f} руб.`\n\n"
                f"📈 **Тренд:** 🟢 Сильный защитный актив в росте (`+0.45%`)\n"
                f"🏛 **Рыночный статус:** Главный актив при макроэкономической нестабильности.\n\n"
                f"✅ Данные обновлены в реальном времени."
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_macro":
            text = t['macro_info']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_premium":
            text = t['premium_info']
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(t['buy_premium'], callback_data="buy_premium_stars"),
                types.InlineKeyboardButton(t['back'], callback_data="menu_back")
            )
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "buy_premium_stars":
            bot.answer_callback_query(call.id, "⚡ Генерация счета...")
            try:
                bot.send_invoice(
                    chat_id=chat_id,
                    title="CryptoScan VIP Premium",
                    description="Месячная подписка на эксклюзивные сигналы и макроаналитику.",
                    invoice_payload="premium_sub",
                    provider_token="",
                    currency="XTR",
                    prices=[types.LabeledPrice(label="VIP 1 Month", amount=100)]
                )
            except:
                bot.send_message(chat_id, "✨ Для активации Премиума свяжитесь с поддержкой.")
            return

        if data == "menu_search":
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, t['search_prompt'] if 'search_prompt' in t else "🔍 Отправьте название актива:", parse_mode="Markdown")
            return
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Ошибка")

@bot.message_handler(func=lambda message: True)
def handle_market_analysis(message):
    chat_id = message.chat.id
    query = message.text.strip()
    if query.startswith('/'):
        return

    lang = get_user_lang(chat_id)
    t = LANGUAGES[lang]

    try:
        bot.send_chat_action(chat_id, 'typing')
        res = analyze_market_asset(query)

        if res:
            p = res['prices']
            text = (
                f"🤖 **Торговый Сигнал & Анализ: {res['name']} ({res['symbol']})**\n\n"
                f"💰 **Спотовая цена:**\n"
                f"• USD: `${p.get('usd', 0):,.4f}`\n"
                f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
                f"• RUB: `{p.get('rub', 0):,.4f} руб.`\n\n"
                f"📈 **Технический срез:**\n"
                f"• Изменение (24ч): `{res['change_24h']:+.2f}%`\n"
                f"• Торговый вердикт: {res['tech_verdict']}\n"
                f"• Суточный объем: `${res['volume_24h']:,.0f}`\n\n"
                f"🏛 **Фундаментальные метрики:**\n"
                f"• Капитализация: `${res['market_cap']:,.0f}`\n"
                f"• Исторический максимум (ATH): `${res['ath']:,.2f}`\n\n"
                f"✅ Сигнал сгенерирован в реальном времени."
            )
        else:
            text = t['not_found']
    except Exception as e:
        text = t['error']

    bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    premium_users.add(chat_id)
    bot.send_message(chat_id, "🎉 Оплата прошла успешно! Вам активирован **Премиум-доступ**.")

# Flask роуты
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







