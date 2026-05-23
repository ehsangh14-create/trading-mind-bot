import os
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TZ = ZoneInfo("America/Vancouver")
DATA_FILE = "life_data.json"
SYMBOLS_FILE = "symbols.json"

# -----------------------------
# Life OS data
# -----------------------------

DEFAULT_TRADING_SYMBOLS = {
    "xauusd": "XAUUSD / طلا",
    "eurusd": "EURUSD",
    "usdjpy": "USDJPY",
    "nasdaq": "NASDAQ",
    "btc": "BTC / کریپتو"
}

TRADING_SUBS = {
    "analysis": "تحلیل",
    "live": "معامله زنده",
    "journal": "ژورنال معامله",
    "backtest": "بک‌تست"
}

BASE_ACTIVITIES = {
    "study": {
        "title": "📚 مطالعه",
        "subjects": {
            "cpa": {
                "title": "CPA",
                "subs": {
                    "fr": "Financial Reporting / مالی",
                    "tax": "Taxation / مالیات",
                    "audit": "Audit / حسابرسی",
                    "mgmt": "Management / مدیریت"
                }
            },
            "english": {
                "title": "English / انگلیسی",
                "subs": {
                    "grammar": "Grammar",
                    "speaking": "Speaking",
                    "listening": "Listening",
                    "vocab": "Vocabulary"
                }
            },
            "python": {
                "title": "Python / پایتون",
                "subs": {
                    "basic": "Basics",
                    "finance": "Finance Analysis",
                    "bot": "Telegram Bot"
                }
            }
        }
    },
    "uber": {
        "title": "🚗 اوبر",
        "subjects": {
            "drive": {
                "title": "Driving / رانندگی",
                "subs": {
                    "work": "Work Shift",
                    "airport": "Airport",
                    "city": "City"
                }
            }
        }
    },
    "walk": {
        "title": "🚶 پیاده‌روی",
        "subjects": {
            "walk": {
                "title": "Walking",
                "subs": {
                    "normal": "Normal Walk",
                    "fast": "Fast Walk",
                    "family": "Family Walk"
                }
            }
        }
    },
    "sleep": {
        "title": "😴 خواب",
        "subjects": {
            "sleep": {
                "title": "Sleep",
                "subs": {
                    "night": "Night Sleep",
                    "nap": "Nap"
                }
            }
        }
    }
}

# -----------------------------
# Trading Mind Master messages
# -----------------------------

MIND_MESSAGES = {
    "mind_trick": [
        "🧠 فریب ذهن\n\nذهن می‌خواهد دائم در بازار باشد؛ اما بازار کار خودش را می‌کند. تو نباید دائم در بازار باشی.",
        "🧠 فریب ذهن\n\nذهن به‌راحتی فریب یک شمع بلند را می‌خورد. شمع بلند دلیل ورود نیست.",
        "🧠 فریب ذهن\n\nهر وقت حس کردی باید همین الآن معامله کنی، اول بپرس: این سیستم است یا اضطراب؟",
        "🧠 فریب ذهن\n\nچارت را باز کن، اما اجازه نده چارت تو را باز کند."
    ],
    "fear": [
        "😨 ترس\n\nاگر حد زیان داری، دلیلی برای وحشت نیست.",
        "😨 ترس\n\nاز حد زیان نترس. از معامله بدون حد زیان بترس.",
        "😨 ترس\n\nاگر می‌ترسی، حجم را کم کن؛ اما قانون را نشکن."
    ],
    "greed": [
        "🔥 طمع\n\nبعد از سود خوب، اقیانوس را ترک کن. دزدهای دریایی منتظر طمع معامله‌گرند.",
        "🔥 طمع\n\nلازم نیست امروز همه سود دنیا را بگیری.",
        "🔥 طمع\n\nطمع یعنی بعد از گرفتن سهم خودت از گنج، باز هم در جزیره بمانی."
    ],
    "patience": [
        "⏳ صبر\n\nفردا هم بازار هست. هفته بعد هم هست. سال بعد هم هست.",
        "⏳ صبر\n\nصبر یعنی حفظ سرمایه برای فرصت بهتر.",
        "⏳ صبر\n\nاگر عجله داری، یعنی آماده معامله نیستی."
    ],
    "samsara": [
        "🔁 سامسارا\n\nضرر → ترس → جبران → حجم بیشتر → ضرر بیشتر.\nچرخه را بازار نساخته؛ ذهن ساخته است.",
        "🔁 سامسارا\n\nرهایی از چرخه یعنی بعد از ضرر، توقف؛ نه انتقام.",
        "🔁 سامسارا\n\nهر بار با همان ذهن قبلی وارد شوی، همان اشتباه قبلی دوباره متولد می‌شود."
    ],
    "watch": [
        "🕊 مشاهده\n\nپنج دقیقه فقط نگاه کن. نه صعودی بگو، نه نزولی. فقط ببین.",
        "🕊 مشاهده\n\nبازار خودش می‌گوید؛ من فقط گوش می‌دهم.",
        "🕊 مشاهده\n\nقبل از ورود، سه نفس عمیق. بعد فقط یک سؤال: سیستم چه می‌گوید؟"
    ],
    "gold": [
        "🏴‍☠️ گنج بازار\n\nبازار یک گنج عظیم است؛ اما فقط برای کسی که نقشه دارد.",
        "🏴‍☠️ گنج\n\nبرای گنج وارد می‌شوم؛ نه برای جنگ. سهمم را برمی‌دارم و برمی‌گردم.",
        "🏴‍☠️ کشتی\n\nحساب تو کشتی توست. برای یک سکه، کشتی را غرق نکن."
    ],
    "walmart": [
        "🏪 والمارت خانگی\n\nتو یک والمارت خانگی داری. والمارت هم همه موجودی‌اش را در یک ساعت نمی‌فروشد.",
        "🏪 مغازه حساب\n\nحساب معاملاتی تو مغازه توست. در یک ساعت مغازه را آتش نزن. فردا هم مشتری هست.",
        "🏪 حفظ مغازه\n\nهدف اول فروش بیشتر نیست؛ هدف اول باز ماندن مغازه است."
    ],
    "business": [
        "💼 بیزینس ترید\n\nترید یک بیزینس است. هر معامله یک تصمیم مدیریتی است، نه هیجان لحظه‌ای.",
        "💼 گردش بزرگ\n\nروزی ۱۰ میلیون دلار می‌توانم معامله کنم؛ اما نه در یک نقطه، نه در یک قیمت، نه در یک لحظه.",
        "💼 مدیریت\n\nمدیر خوب اول ریسک را کنترل می‌کند، بعد دنبال سود می‌رود."
    ],
    "capital": [
        "🛡 سرمایه\n\nسرمایه من فقط عدد حساب نیست؛ اعتماد، بقا و ادامه کسب‌وکار من است.",
        "🛡 ریسک\n\nهمه سرمایه را در یک لحظه در معرض ریسک قرار نمی‌دهم.",
        "🛡 قانون بقا\n\nحساب زنده بماند، فرصت دوباره هست."
    ],
    "setup": [
        "📊 ستاپ کانال و میانگین\n\n۱. جهت تایم بالا مشخص شود.\n۲. کانال رسم شود.\n۳. میانگین‌ها بررسی شود.\n۴. ورود فقط روی اصلاح.\n۵. حد زیان کوچک.\n۶. خروج سریع.",
        "📊 نقشه معامله\n\nکانال، میانگین، روند، حجم و حد زیان نقشه گنج معامله‌اند."
    ],
    "channel": [
        "📐 کانال\n\nکف کانال در روند صعودی، محل جستجوی خرید است.\nسقف کانال در روند نزولی، محل جستجوی فروش است.",
        "📐 کانال\n\nدر روند صعودی دنبال کف باش، نه سقف. در روند نزولی دنبال سقف باش، نه کف."
    ],
    "ma": [
        "〽️ میانگین‌ها\n\nمیانگین‌ها زبان بازارند. قیمت به میانگین‌ها واکنش می‌دهد.",
        "〽️ میانگین‌ها\n\nواکنش قیمت به میانگین را ببین؛ حدس نزن."
    ],
    "buy": [
        "📈 خرید حرفه‌ای\n\nدر روند صعودی، روی اصلاح و کف کانال خرید کن؛ نه وسط هیجان شمع بلند.",
        "📈 خرید\n\nخرید در سقف ممنوع. خرید بعد از شمع بلند هیجانی ممنوع."
    ],
    "sell": [
        "📉 فروش حرفه‌ای\n\nدر روند نزولی، روی اصلاح و سقف کانال فروش کن؛ نه بعد از ریزش شدید.",
        "📉 فروش\n\nفروش در کف ممنوع. فروش بعد از ریزش شدید، اغلب دیر است."
    ],
    "entry_exit": [
        "⚡ ورود و خروج سریع\n\nورود خوب باید سریع وارد سود شود. اگر حرکت نکرد، شاید جای ورود اشتباه بوده.",
        "⚡ خروج حرفه‌ای\n\nخروج خوب گاهی مهم‌تر از ورود خوب است. سود گرفتی، محافظت کن.",
        "⚡ سود روزانه\n\nسود روزانه را می‌گیرم، چارت را می‌بندم، تا روز بعد."
    ],
    "volume": [
        "⚖️ حجم\n\nنه در یک نقطه، نه در یک قیمت، نه در یک لحظه، همه حجم را وارد نکن.",
        "⚖️ تقسیم حجم\n\nاگر قرار است سه لات معامله کنی، آن را در چند نقطه منطقی پخش کن.",
        "⚖️ ممنوع\n\nهیچ‌وقت به معامله زیان‌ده برای جبران، حجم اضافه نکن."
    ],
    "sl": [
        "🛑 حد زیان\n\nحد زیان یعنی: من اشتباه بودن را می‌پذیرم و حسابم را حفظ می‌کنم.",
        "🛑 حد زیان\n\nزیان باید کوچک، کنترل‌شده و قابل پذیرش باشد."
    ],
    "loss": [
        "📉 زیان\n\nبرای جبران یک اشتباه، اشتباه بزرگ‌تر نکن.",
        "📉 زیان\n\nزیان امروز را به فاجعه امروز تبدیل نکن. فردا هم هست."
    ],
    "profit": [
        "📈 سود\n\nسود خوب کردی؟ چارت را ببند. برگرد به زندگی.",
        "📈 سود\n\nسود کوچکِ تکرارشونده، بهتر از سود بزرگِ شانسی است."
    ],
    "checklist": [
        "✅ چک‌لیست ورود\n\n۱. جهت تایم بالا مشخص است؟\n۲. کانال رسم شده؟\n۳. میانگین‌ها تایید می‌کنند؟\n۴. ورود روی اصلاح است؟\n۵. حد زیان کوچک است؟\n۶. حجم مناسب است؟",
        "✅ قبل از ورود\n\nآیا این معامله حفظ کسب‌وکار است یا تلاش برای جبران؟"
    ]
}

# -----------------------------
# Helpers
# -----------------------------

def normalize_symbol(symbol):
    return symbol.strip().upper().replace("/", "").replace(" ", "")

def symbol_key(symbol):
    return normalize_symbol(symbol).lower()

def load_symbols():
    if not os.path.exists(SYMBOLS_FILE):
        save_symbols(DEFAULT_TRADING_SYMBOLS)
        return dict(DEFAULT_TRADING_SYMBOLS)
    with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        data = dict(DEFAULT_TRADING_SYMBOLS)
        save_symbols(data)
    return data

def save_symbols(symbols):
    with open(SYMBOLS_FILE, "w", encoding="utf-8") as f:
        json.dump(symbols, f, ensure_ascii=False, indent=2)

def get_activities():
    activities = json.loads(json.dumps(BASE_ACTIVITIES, ensure_ascii=False))
    subjects = {}
    for key, title in load_symbols().items():
        subjects[key] = {"title": title, "subs": TRADING_SUBS}
    activities["trading"] = {"title": "📊 ترید عملی", "subjects": subjects}
    return activities

def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")

def parse_dt(s):
    return datetime.fromisoformat(s)

def fmt_duration(seconds):
    minutes = int(float(seconds) // 60)
    h = minutes // 60
    m = minutes % 60
    if h and m:
        return f"{h} ساعت و {m} دقیقه"
    if h:
        return f"{h} ساعت"
    return f"{m} دقیقه"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"active": {}, "sessions": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def random_mind_message():
    all_messages = []
    for items in MIND_MESSAGES.values():
        all_messages.extend(items)
    return random.choice(all_messages)

# -----------------------------
# Menus
# -----------------------------

def root_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏴‍☠️ Trading Mind Master", callback_data="root:mind")],
        [InlineKeyboardButton("🧠 Personal Life OS", callback_data="root:life")]
    ])

def mind_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 ذهن حرفه‌ای", callback_data="mind_menu:psych")],
        [InlineKeyboardButton("🏴‍☠️ گنج و بیزینس", callback_data="mind_menu:business")],
        [InlineKeyboardButton("📊 ستاپ معامله", callback_data="mind_menu:setup")],
        [InlineKeyboardButton("🛡 مدیریت ریسک", callback_data="mind_menu:risk")],
        [InlineKeyboardButton("🎲 پیام تصادفی از همه", callback_data="mind_random")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="root")]
    ])

def mind_menu_psych():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 فریب ذهن", callback_data="mind_msg:mind_trick"), InlineKeyboardButton("😨 ترس", callback_data="mind_msg:fear")],
        [InlineKeyboardButton("🔥 طمع", callback_data="mind_msg:greed"), InlineKeyboardButton("⏳ صبر", callback_data="mind_msg:patience")],
        [InlineKeyboardButton("🔁 سامسارا", callback_data="mind_msg:samsara"), InlineKeyboardButton("🕊 مشاهده", callback_data="mind_msg:watch")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="root:mind")]
    ])

def mind_menu_business():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏴‍☠️ گنج بازار", callback_data="mind_msg:gold"), InlineKeyboardButton("🏪 والمارت", callback_data="mind_msg:walmart")],
        [InlineKeyboardButton("💼 بیزینس ترید", callback_data="mind_msg:business"), InlineKeyboardButton("🛡 سرمایه", callback_data="mind_msg:capital")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="root:mind")]
    ])

def mind_menu_setup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ستاپ کلی", callback_data="mind_msg:setup"), InlineKeyboardButton("📐 کانال", callback_data="mind_msg:channel")],
        [InlineKeyboardButton("〽️ میانگین‌ها", callback_data="mind_msg:ma"), InlineKeyboardButton("⚡ ورود/خروج", callback_data="mind_msg:entry_exit")],
        [InlineKeyboardButton("📈 خرید", callback_data="mind_msg:buy"), InlineKeyboardButton("📉 فروش", callback_data="mind_msg:sell")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="root:mind")]
    ])

def mind_menu_risk():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚖️ حجم", callback_data="mind_msg:volume"), InlineKeyboardButton("🛑 حد زیان", callback_data="mind_msg:sl")],
        [InlineKeyboardButton("📉 زیان", callback_data="mind_msg:loss"), InlineKeyboardButton("📈 سود", callback_data="mind_msg:profit")],
        [InlineKeyboardButton("✅ چک‌لیست", callback_data="mind_msg:checklist")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="root:mind")]
    ])

def life_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 مطالعه", callback_data="activity:study")],
        [InlineKeyboardButton("📊 ترید عملی", callback_data="activity:trading")],
        [InlineKeyboardButton("🚗 اوبر", callback_data="activity:uber")],
        [InlineKeyboardButton("🚶 پیاده‌روی", callback_data="activity:walk")],
        [InlineKeyboardButton("😴 خواب", callback_data="activity:sleep")],
        [InlineKeyboardButton("➕ افزودن نماد: /addsymbol GBPJPY", callback_data="help:addsymbol")],
        [InlineKeyboardButton("📊 گزارش امروز", callback_data="report:today")],
        [InlineKeyboardButton("⏹ پایان فعالیت فعال", callback_data="stop:active")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="root")]
    ])

def subject_menu(activity_key):
    activities = get_activities()
    rows = []
    for subject_key, subject in activities[activity_key]["subjects"].items():
        rows.append([InlineKeyboardButton(subject["title"], callback_data=f"subject:{activity_key}:{subject_key}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data="root:life")])
    return InlineKeyboardMarkup(rows)

def sub_menu(activity_key, subject_key):
    activities = get_activities()
    rows = []
    for sub_key, sub_title in activities[activity_key]["subjects"][subject_key]["subs"].items():
        rows.append([InlineKeyboardButton(sub_title, callback_data=f"sub:{activity_key}:{subject_key}:{sub_key}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data=f"activity:{activity_key}")])
    return InlineKeyboardMarkup(rows)

def start_stop_menu(activity_key, subject_key, sub_key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ شروع", callback_data=f"startsession:{activity_key}:{subject_key}:{sub_key}")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data=f"subject:{activity_key}:{subject_key}")],
        [InlineKeyboardButton("🏠 Life OS", callback_data="root:life")]
    ])

# -----------------------------
# Commands
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سیستم اصلی:\n\n🏴‍☠️ Trading Mind Master\n🧠 Personal Life OS\n\nیکی را انتخاب کن:",
        reply_markup=root_menu()
    )

async def add_symbol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال:\n/addsymbol GBPJPY\n/addsymbol US30\n/addsymbol ETH")
        return

    symbol = normalize_symbol(" ".join(context.args))
    if not symbol:
        await update.message.reply_text("نماد معتبر نیست.")
        return

    key = symbol_key(symbol)
    symbols = load_symbols()
    if key in symbols:
        await update.message.reply_text(f"این نماد قبلاً وجود دارد: {symbols[key]}")
        return

    symbols[key] = symbol
    save_symbols(symbols)
    await update.message.reply_text(f"✅ نماد اضافه شد: {symbol}\nحالا در بخش 📊 ترید عملی می‌بینی.", reply_markup=life_main_menu())

async def list_symbols_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbols = load_symbols()
    text = "📊 نمادهای ترید عملی:\n\n" + "\n".join([f"• {v}" for v in symbols.values()])
    await update.message.reply_text(text)

async def remove_symbol_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("مثال:\n/removesymbol GBPJPY")
        return

    symbol = normalize_symbol(" ".join(context.args))
    key = symbol_key(symbol)
    symbols = load_symbols()

    if key not in symbols:
        await update.message.reply_text("این نماد در لیست نیست.")
        return

    removed = symbols.pop(key)
    save_symbols(symbols)
    await update.message.reply_text(f"🗑 نماد حذف شد: {removed}", reply_markup=life_main_menu())

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random_mind_message())

async def report_today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_today_report(update.message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - منوی اصلی\n"
        "/today - گزارش امروز Life OS\n"
        "/random - پیام تصادفی مایندست\n"
        "/addsymbol GBPJPY - افزودن نماد\n"
        "/removesymbol GBPJPY - حذف نماد\n"
        "/symbols - لیست نمادها\n"
        "/help - راهنما"
    )

# -----------------------------
# Button handler
# -----------------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    activities = get_activities()

    if data == "root":
        await query.message.reply_text("🏠 منوی اصلی:", reply_markup=root_menu())
        return

    if data == "root:mind":
        await query.message.reply_text("🏴‍☠️ Trading Mind Master:", reply_markup=mind_main_menu())
        return

    if data == "root:life":
        await query.message.reply_text("🧠 Personal Life OS:", reply_markup=life_main_menu())
        return

    if data == "mind_menu:psych":
        await query.message.reply_text("🧠 ذهن حرفه‌ای:", reply_markup=mind_menu_psych())
        return

    if data == "mind_menu:business":
        await query.message.reply_text("🏴‍☠️ گنج و بیزینس:", reply_markup=mind_menu_business())
        return

    if data == "mind_menu:setup":
        await query.message.reply_text("📊 ستاپ معامله:", reply_markup=mind_menu_setup())
        return

    if data == "mind_menu:risk":
        await query.message.reply_text("🛡 مدیریت ریسک:", reply_markup=mind_menu_risk())
        return

    if data == "mind_random":
        await query.message.reply_text(random_mind_message(), reply_markup=mind_main_menu())
        return

    if data.startswith("mind_msg:"):
        key = data.split(":")[1]
        text = random.choice(MIND_MESSAGES.get(key, ["موردی پیدا نشد."]))
        await query.message.reply_text(text)
        return

    if data == "help:addsymbol":
        await query.message.reply_text("برای افزودن نماد بنویس:\n/addsymbol GBPJPY\n\nبرای دیدن لیست:\n/symbols")
        return

    if data.startswith("activity:"):
        activity_key = data.split(":")[1]
        await query.message.reply_text(f"{activities[activity_key]['title']}\nموضوع را انتخاب کن:", reply_markup=subject_menu(activity_key))
        return

    if data.startswith("subject:"):
        _, activity_key, subject_key = data.split(":")
        title = activities[activity_key]["subjects"][subject_key]["title"]
        await query.message.reply_text(f"📌 {title}\nزیرموضوع را انتخاب کن:", reply_markup=sub_menu(activity_key, subject_key))
        return

    if data.startswith("sub:"):
        _, activity_key, subject_key, sub_key = data.split(":")
        activity_title = activities[activity_key]["title"]
        subject_title = activities[activity_key]["subjects"][subject_key]["title"]
        sub_title = activities[activity_key]["subjects"][subject_key]["subs"][sub_key]
        await query.message.reply_text(
            f"{activity_title}\nموضوع: {subject_title}\nزیرموضوع: {sub_title}\n\nبرای شروع بزن:",
            reply_markup=start_stop_menu(activity_key, subject_key, sub_key)
        )
        return

    if data.startswith("startsession:"):
        _, activity_key, subject_key, sub_key = data.split(":")
        user_id = str(query.from_user.id)
        store = load_data()

        if user_id in store["active"]:
            active = store["active"][user_id]
            await query.message.reply_text(
                "⚠️ یک فعالیت فعال داری. اول آن را پایان بده:\n\n"
                f"{active['activity_title']} / {active['subject_title']} / {active['sub_title']}",
                reply_markup=life_main_menu()
            )
            return

        start_time = now_iso()
        active_session = {
            "activity": activity_key,
            "subject": subject_key,
            "sub": sub_key,
            "activity_title": activities[activity_key]["title"],
            "subject_title": activities[activity_key]["subjects"][subject_key]["title"],
            "sub_title": activities[activity_key]["subjects"][subject_key]["subs"][sub_key],
            "start_time": start_time
        }
        store["active"][user_id] = active_session
        save_data(store)

        await query.message.reply_text(
            "▶️ فعالیت شروع شد:\n\n"
            f"{active_session['activity_title']}\n"
            f"موضوع: {active_session['subject_title']}\n"
            f"زیرموضوع: {active_session['sub_title']}\n"
            f"زمان شروع: {parse_dt(start_time).strftime('%Y-%m-%d %H:%M')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏹ پایان", callback_data="stop:active")],
                [InlineKeyboardButton("🏠 Life OS", callback_data="root:life")]
            ])
        )
        return

    if data == "stop:active":
        user_id = str(query.from_user.id)
        store = load_data()

        if user_id not in store["active"]:
            await query.message.reply_text("فعالیت فعالی برای پایان دادن وجود ندارد.", reply_markup=life_main_menu())
            return

        active = store["active"].pop(user_id)
        end_time = now_iso()
        start_dt = parse_dt(active["start_time"])
        end_dt = parse_dt(end_time)
        duration_seconds = (end_dt - start_dt).total_seconds()

        session = dict(active)
        session.update({
            "end_time": end_time,
            "duration_seconds": duration_seconds,
            "date": start_dt.strftime("%Y-%m-%d")
        })
        store["sessions"].append(session)
        save_data(store)

        await query.message.reply_text(
            "⏹ فعالیت پایان یافت:\n\n"
            f"{active['activity_title']}\n"
            f"موضوع: {active['subject_title']}\n"
            f"زیرموضوع: {active['sub_title']}\n"
            f"شروع: {start_dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"پایان: {end_dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"مدت: {fmt_duration(duration_seconds)}",
            reply_markup=life_main_menu()
        )
        return

    if data == "report:today":
        await send_today_report(query.message)
        return

# -----------------------------
# Reports
# -----------------------------

async def send_today_report(message):
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    store = load_data()
    sessions = [s for s in store["sessions"] if s.get("date") == today]

    if not sessions:
        await message.reply_text("برای امروز هنوز فعالیتی ثبت نشده.", reply_markup=life_main_menu())
        return

    totals = {}
    for s in sessions:
        key = f"{s['activity_title']} / {s['subject_title']} / {s['sub_title']}"
        totals[key] = totals.get(key, 0) + float(s["duration_seconds"])

    lines = [f"📊 گزارش امروز - {today}\n"]
    for key, seconds in totals.items():
        lines.append(f"• {key}: {fmt_duration(seconds)}")

    await message.reply_text("\n".join(lines), reply_markup=life_main_menu())

# -----------------------------
# App
# -----------------------------

async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "منوی اصلی"),
        BotCommand("today", "گزارش امروز Life OS"),
        BotCommand("random", "پیام تصادفی مایندست"),
        BotCommand("addsymbol", "افزودن نماد"),
        BotCommand("removesymbol", "حذف نماد"),
        BotCommand("symbols", "لیست نمادها"),
        BotCommand("help", "راهنما")
    ])

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", report_today_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("addsymbol", add_symbol_command))
    app.add_handler(CommandHandler("removesymbol", remove_symbol_command))
    app.add_handler(CommandHandler("symbols", list_symbols_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Combined Trading Mind + Life OS Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
