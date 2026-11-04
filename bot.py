import os
import telebot
from telebot import types
from flask import Flask, request

requests = None
try:
    import requests
except ImportError:
    pass

# Твой актуальный токен бота
TOKEN = '9223957380:AAEkwjCuZcLfVxK0HM87HHyNZZ73Mxl7mYw'
bot = telebot.TeleBot(TOKEN)

server = Flask(__name__)

# Мультиязычные тексты, гиды для новичков и Премиум
LANGUAGES = {
    'uz': {
        'welcome': "👋 **Assalomu alaykum! Global halol spot va treyding servisiga xush kelibsiz.**\n\nIltimos, o'zingizga qulay tilni tanlang:",
        'guide_btn': "📖 Botdan qanday foydalanish? (Qo'llanma)",
        'choose_action': "👇 Kerakli bo'limni tanlang:",
        'btn_btc': "🪙 Bitcoin narxi va tahlili",
        'btn_gold': "🥇 Oltin (XAU/USD)",
        'btn_nfp': "📰 Muhim yangiliklar (NFP / Makro)",
        'btn_search': "🔍 Istalgan aktivni tahlil qilish",
        'btn_premium': "💎 Premium imkoniyatlar",
        'btn_lang': "🌐 Tilni o'zgartirish",
        'guide_text': (
            "📖 **Botdan foydalanish bo'yicha qo'llanma (Yangi foydalanuvchilar uchun):**\n\n"
            "Bu bot — dunyodagi istalgan kriptovalyuta, oltin va aktivlarning **halol spot narxlarini** real vaqt rejimida kuzatish va tahlil qilish uchun ishonchli yordamchi.\n\n"
            "✨ **Siz nima qila olasiz?**\n"
            "1. **Asosiy aktivlar:** Bitcoin va oltin narxlarini bir tugma orqali ko'ring.\n"
            "2. **Erkin qidiruv / Tahlil:** Chatga istalgan tanga nomini (masalan: `ethereum`, `solana`, `ton`, `ripple`) yozing — bot uning narxini USD, UZS (so'm), RUB da va texnik tahlilini darhol chiqarib beradi!\n"
            "3. **Makroiqtisodiyot:** NFP kabi muhim dunyo yangiliklaridan xabardor bo'ling.\n"
            "4. **Premium:** Professional treyderlar uchun qo'shimcha imkoniyatlarni oching.\n\n"
            "👇 Asosiy menyudan kerakli bo'limni tanlang!"
        ),
        'btc_info': "🪙 **Bitcoin (BTC) - Spot Tahlili**\n\n📈 **Joriy narx:**",
        'gold_info': "🥇 **Oltin (XAU/USD)** — jahon bozoridagi eng ishonchli aktiv.\n\n📈 **Spot narxi:**",
        'nfp_info': (
            "📰 **Muhim Makroiqtisodiy Yangiliklar va NFP**\n\n"
            "📉 **NFP (Non-Farm Payrolls)** — AQSh ish o'rinlari statistikasi. Oltin, dollar (Forex) va barcha kriptovalyutalarga kuchli ta'sir qiladi!\n\n"
            "⚠️ **Eslatma:** Halol spot savdosida xavfni boshqarish juda muhim."
        ),
        'search_prompt': "🔍 **Bozorni avtomatik tahlil qilish**\n\nIltimos, istalgan aktiv nomini yozib yuboring (masalan: `bitcoin`, `ethereum`, `gold`, `solana`):",
        'premium_info': (
            "💎 **Premium Imkoniyatlar va Imtiyozlar**\n\n"
            "Agar siz professional darajada savdo qilishni va ko'proq foyda olishni istasangiz, **Premium** sizga quyidagilarni taqdim etadi:\n\n"
            "🚀 **1. Shaxsiy Portfel:** O'z aktivlaringizni yagona tizimda kuzatib boring.\n"
            "🔔 **2. Smart-Alerts (Bildirishnomalar):** Tanga siz kutgan narxga yetganda bot sizga darhol maxsus signal yuboradi.\n"
            "📊 **3. Chuqur Texnik Tahlil:** Bozorning qo'llab-quvvatlash va qarshilik darajalari.\n"
            "🚫 **4. Mutlaqo reklamasiz muhit.**\n\n"
            "✨ *Moliyaviy imkoniyatlaringizni oshirish uchun Premium-ga ulaning! Batafsil ma'lumot uchun administratorga yozing.*"
        ),
        'not_found': "❌ Kechirasiz, bu so'rov bo'yicha ma'lumot topilmadi. Iltimos, aktiv nomini to'g'ri yozing (masalan: `bitcoin`, `solana`, `ethereum`).",
        'error': "⚠️ Texnik xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
        'back': "🔙 Asosiy menyu"
    },
    'ru': {
        'welcome': "👋 **Ассалому алайкум! Добро пожаловать в глобальный спот и трейдинг сервис.**\n\nПожалуйста, выберите язык:",
        'guide_btn': "📖 Как пользоваться ботом? (Гид)",
        'choose_action': "👇 Выберите нужный раздел:",
        'btn_btc': "🪙 Цена Биткоина и анализ",
        'btn_gold': "🥇 Золото (XAU/USD)",
        'btn_nfp': "📰 Важные новости (NFP / Макро)",
        'btn_search': "🔍 Анализ любого актива",
        'btn_premium': "💎 Премиум возможности",
        'btn_lang': "🌐 Изменить язык",
        'guide_text': (
            "📖 **Гид по использованию бота (Для новых пользователей):**\n\n"
            "Этот бот создан как универсальный, честный и чистый помощник для мониторинга **спотовых цен** на криптовалюты, золото и активы без риба и скрытых условий.\n\n"
            "✨ **Что вы можете делать?**\n"
            "1. **Быстрые цены:** Узнавайте курс Биткоина и золота в один клик.\n"
            "2. **Умный поиск и анализ:** Просто напишите в чат название любой монеты (например: `ethereum`, `solana`, `ripple`, `ton`), и бот мгновенно выдаст её курс в USD, сумах (UZS), рублях (RUB) и технический вердикт!\n"
            "3. **Макро-новости:** Следите за отчетами NFP и ключевыми событиями рынка.\n"
            "4. **Премиум:** Получите профессиональные инструменты трейдера.\n\n"
            "👇 Выберите нужный пункт в меню ниже!"
        ),
        'btc_info': "🪙 **Биткоин (Bitcoin / BTC) - Спот-анализ**\n\n📈 **Текущая цена:**",
        'gold_info': "🥇 **Золото (XAU/USD)** — мировой защитный актив.\n\n📈 **Спотовая цена:**",
        'nfp_info': (
            "📰 **Макроэкономический календарь и новости (NFP)**\n\n"
            "📉 **NFP (Non-Farm Payrolls)** — важнейший отчет США, вызывающий мощнейшие движения на рынках **Forex**, **Золота** и **Криптовалюты**!\n\n"
            "⚠️ **Совет:** Соблюдайте риск-менеджмент."
        ),
        'search_prompt': "🔍 **Автоматический анализ рынка**\n\nПожалуйста, отправьте название любого актива (например: `bitcoin`, `ethereum`, `gold`, `solana`):",
        'premium_info': (
            "💎 **Премиум-доступ и привилегии для трейдеров**\n\n"
            "Приобретая **Премиум**, вы получаете эксклюзивный набор профессиональных инструментов для максимизации результатов:\n\n"
            "🚀 **1. Личный крипто-портфель:** Удобный учет ваших сбережений в реальном времени.\n"
            "🔔 **2. Умные ценовые алерты:** Автоматические уведомления, когда актив достигает вашей цели.\n"
            "📊 **3. Расширенный технический анализ:** Дополнительные индикаторы и уровни.\n"
            "🚫 **4. Полное отсутствие рекламы** и приоритетная поддержка.\n\n"
            "✨ *Инвестируйте в свои возможности! Свяжитесь с поддержкой для активации Премиума.*"
        ),
        'not_found': "❌ К сожалению, по вашему запросу ничего не найдено. Проверьте правильность написания (например: `bitcoin`, `ethereum`, `solana`).",
        'error': "⚠️ Ошибка при обработке запроса. Попробуйте еще раз.",
        'back': "🔙 Главное меню"
    },
    'en': {
        'welcome': "👋 **Welcome to Global Spot & Trading Service.**\n\nPlease select your language:",
        'guide_btn': "📖 How to use the bot? (Guide)",
        'choose_action': "👇 Choose a section:",
        'btn_btc': "🪙 Bitcoin Price & Analysis",
        'btn_gold': "🥇 Gold (XAU/USD)",
        'btn_nfp': "📰 Market News (NFP / Macro)",
        'btn_search': "🔍 Analyze Any Asset",
        'btn_premium': "💎 Premium Features",
        'btn_lang': "🌐 Change Language",
        'guide_text': (
            "📖 **User Guide (For Newcomers):**\n\n"
            "This bot is your clean, transparent assistant for tracking **spot prices** of cryptocurrencies and gold.\n\n"
            "✨ **Features:**\n"
            "1. Quick access to Bitcoin and Gold prices.\n"
            "2. Type any coin name (e.g., `ethereum`, `solana`) to get instant spot analysis.\n"
            "3. Macro news & NFP calendar.\n"
            "4. Premium tools for traders."
        ),
        'btc_info': "🪙 **Bitcoin (BTC) - Spot Analysis**\n\n📈 **Current Price:**",
        'gold_info': "🥇 **Gold (XAU/USD)** — global safe-haven asset.\n\n📈 **Spot Price:**",
        'nfp_info': "📰 **Macro News & NFP Calendar**\n\nNon-Farm Payrolls massively impact global markets.",
        'search_prompt': "🔍 **Automated Market Analysis**\n\nSend any asset name or ticker (e.g., `bitcoin`, `ethereum`, `gold`):",
        'premium_info': (
            "💎 **Trader Premium Benefits**\n\n"
            "Upgrade to **Premium** to unlock professional tools:\n\n"
            "🚀 **1. Personal Portfolio:** Track all your holdings in one place.\n"
            "🔔 **2. Price Alerts:** Instant notifications when targets are hit.\n"
            "📊 **3. Deep Tech Analytics:** Advanced market indicators.\n"
            "🚫 **4. Ad-free experience.**\n\n"
            "✨ *Contact support to upgrade your account today!*"
        ),
        'not_found': "❌ Nothing found. Please check your spelling.",
        'error': "⚠️ An error occurred. Try again later.",
        'back': "🔙 Main Menu"
    },
    'tr': {
        'welcome': "👋 **Küresel Spot ve Ticaret Servisine Hoş Geldiniz.**\n\nDilinizi seçin:",
        'guide_btn': "📖 Bot Nasıl Kullanılır? (Rehber)",
        'choose_action': "👇 Bir bölüm seçin:",
        'btn_btc': "🪙 Bitcoin Fiyatı ve Analizi",
        'btn_gold': "🥇 Altın (XAU/USD)",
        'btn_nfp': "📰 Makro Haberler (NFP)",
        'btn_search': "🔍 Varlık Analizi Yap",
        'btn_premium': "💎 Premium Özellikler",
        'btn_lang': "🌐 Dili Değiştir",
        'guide_text': (
            "📖 **Kullanıcı Rehberi (Yeni Başlayanlar İçin):**\n\n"
            "Bu bot, kripto para, altın ve varlıkların **spot fiyatlarını** güvenle takip etmeniz için tasarlanmıştır.\n\n"
            "✨ İstediğiniz coinin adını yazarak anında analiz alabilirsiniz!"
        ),
        'btc_info': "🪙 **Bitcoin (BTC) - Spot Analiz**\n\n📈 **Güncel Fiyat:**",
        'gold_info': "🥇 **Altın (XAU/USD)**\n\n📈 **Spot Fiyat:**",
        'nfp_info': "📰 **NFP ve Makroekonomik Takvim**\n\nKüresel piyasaları etkileyen önemli veriler.",
        'search_prompt': "🔍 **Otomatik Piyasa Analizi**\n\nLütfen bir varlık adı gönderin (ör: `bitcoin`, `ethereum`):",
        'premium_info': (
            "💎 **Trader Premium Ayrıcalıkları**\n\n"
            "🚀 **1. Kişisel Portföy**\n🔔 **2. Fiyat Alarmları**\n📊 **3. Derin Analiz**\n🚫 **4. Reklamsız Deneyim**\n\n✨ *Aktivasyon için iletişime geçin.*"
        ),
        'not_found': "❌ Bulunamadı. Doğru yazdığınızdan emin olun.",
        'error': "⚠️ Hata oluştu.",
        'back': "🔙 Ana Menü"
    }
}

user_languages = {}

def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'uz')

def analyze_market_asset(query):
    try:
        query = query.strip().lower()
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
        prices = market_data.get('current_price', {})
        change_24h = market_data.get('price_change_percentage_24h', 0) or 0
        volume_24h = market_data.get('total_volume', {}).get('usd', 0) or 0
        market_cap = market_data.get('market_cap', {}).get('usd', 0) or 0
        ath = market_data.get('ath', {}).get('usd', 0) or 0

        if change_24h > 3:
            tech_verdict = "🟢 Сильный импульс (Бычий тренд)"
        elif change_24h > 0:
            tech_verdict = "🟢 Умеренный рост"
        elif change_24h > -3:
            tech_verdict = "🟡 Консолидация / Коррекция"
        else:
            tech_verdict = "🔴 Медвежья фаза (Давление продавцов)"

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
        return res.get('price')
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")
    )
    text = "🌍 **Global Spot & Trading Terminal**\n\nSelect language / Tilni tanlang / Выберите язык:"
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

def show_main_menu(chat_id, message_id=None):
    lang = get_user_lang(chat_id)
    t = LANGUAGES[lang]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t['guide_btn'], callback_data="menu_guide"),
        types.InlineKeyboardButton(t['btn_btc'], callback_data="menu_btc"),
        types.InlineKeyboardButton(t['btn_gold'], callback_data="menu_gold"),
        types.InlineKeyboardButton(t['btn_nfp'], callback_data="menu_nfp"),
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
            text = t['guide_text']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_btc":
            res = analyze_market_asset("bitcoin")
            if res:
                p = res['prices']
                text = (
                    f"{t['btc_info']}\n"
                    f"• USD: `${p.get('usd', 0):,.2f}`\n"
                    f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
                    f"• RUB: `{p.get('rub', 0):,.2f} руб.`\n\n"
                    f"📊 **Анализ:** {res['tech_verdict']} (`{res['change_24h']:+.2f}%`)\n"
                    f"✅ Чистый спот."
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
            if price:
                text = f"{t['gold_info']} `{price:,.2f} USD` (troy oz)\n\n✅ Мировой спот золота."
            else:
                text = t['error']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_nfp":
            text = t['nfp_info']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_premium":
            text = t['premium_info']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t['back'], callback_data="menu_back"))
            bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
            return

        if data == "menu_search":
            text = t['search_prompt']
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, text, parse_mode="Markdown")
            return
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Ошибка обработки")

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
                f"🤖 **Автоматический Анализ: {res['name']} ({res['symbol']})**\n\n"
                f"💰 **Спотовая цена:**\n"
                f"• USD: `${p.get('usd', 0):,.4f}`\n"
                f"• UZS: `{p.get('uzs', 0):,.2f} so'm`\n"
                f"• RUB: `${p.get('rub', 0):,.4f} руб.`\n\n"
                f"📈 **Технический срез:**\n"
                f"• Изменение (24ч): `{res['change_24h']:+.2f}%`\n"
                f"• Вердикт: {res['tech_verdict']}\n"
                f"• Объем торгов: `${res['volume_24h']:,.0f}`\n\n"
                f"🏛 **Фундаментальные метрики:**\n"
                f"• Капитализация рынка: `${res['market_cap']:,.0f}`\n"
                f"• Исторический максимум (ATH): `${res['ath']:,.2f}`\n\n"
                f"✅ Анализ выполнен в реальном времени."
            )
        else:
            text = t['not_found']
    except Exception as e:
        text = t['error']

    bot.send_message(chat_id, text, parse_mode="Markdown")

# Вебхук роутеры для Flask (чтобы Render запускал веб-сервис без конфликтов 409)
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('uz-UZ' if False else 'utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://spot-bot-1.onrender.com/{TOKEN}")
    return "Spot Bot is running on Render!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://spot-bot-1.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))






