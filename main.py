import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MESSAGES = {
    "mind_trick": [
        "🧠 فریب ذهن\n\nذهن می‌خواهد دائم در بازار باشد؛ اما بازار کار خودش را می‌کند. تو نباید دائم در بازار باشی.",
        "🧠 فریب ذهن\n\nذهن به‌راحتی فریب یک شمع بلند را می‌خورد. شمع بلند دلیل ورود نیست.",
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

MAIN_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧠 ذهن حرفه‌ای", callback_data="menu_mind")],
    [InlineKeyboardButton("🏴‍☠️ گنج و بیزینس", callback_data="menu_business")],
    [InlineKeyboardButton("📊 ستاپ معامله", callback_data="menu_setup")],
    [InlineKeyboardButton("🛡 مدیریت ریسک", callback_data="menu_risk")],
    [InlineKeyboardButton("🎲 پیام تصادفی از همه", callback_data="random")]
])

def menu_mind():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 فریب ذهن", callback_data="mind_trick"), InlineKeyboardButton("😨 ترس", callback_data="fear")],
        [InlineKeyboardButton("🔥 طمع", callback_data="greed"), InlineKeyboardButton("⏳ صبر", callback_data="patience")],
        [InlineKeyboardButton("🔁 سامسارا", callback_data="samsara"), InlineKeyboardButton("🕊 مشاهده", callback_data="watch")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="main_menu")]
    ])

def menu_business():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏴‍☠️ گنج بازار", callback_data="gold"), InlineKeyboardButton("🏪 والمارت", callback_data="walmart")],
        [InlineKeyboardButton("💼 بیزینس ترید", callback_data="business"), InlineKeyboardButton("🛡 سرمایه", callback_data="capital")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="main_menu")]
    ])

def menu_setup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ستاپ کلی", callback_data="setup"), InlineKeyboardButton("📐 کانال", callback_data="channel")],
        [InlineKeyboardButton("〽️ میانگین‌ها", callback_data="ma"), InlineKeyboardButton("⚡ ورود/خروج", callback_data="entry_exit")],
        [InlineKeyboardButton("📈 خرید", callback_data="buy"), InlineKeyboardButton("📉 فروش", callback_data="sell")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="main_menu")]
    ])

def menu_risk():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚖️ حجم", callback_data="volume"), InlineKeyboardButton("🛑 حد زیان", callback_data="sl")],
        [InlineKeyboardButton("📉 زیان", callback_data="loss"), InlineKeyboardButton("📈 سود", callback_data="profit")],
        [InlineKeyboardButton("✅ چک‌لیست", callback_data="checklist")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="main_menu")]
    ])

def random_message_from_all_categories():
    all_messages = []
    for items in MESSAGES.values():
        all_messages.extend(items)
    return random.choice(all_messages)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏴‍☠️ گنج بازار | Trading Mind Master\n\nمنوی اصلی:", reply_markup=MAIN_MENU)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.message.reply_text("🏠 منوی اصلی:", reply_markup=MAIN_MENU)
        return
    if data == "menu_mind":
        await query.message.reply_text("🧠 ذهن حرفه‌ای:", reply_markup=menu_mind())
        return
    if data == "menu_business":
        await query.message.reply_text("🏴‍☠️ گنج و بیزینس:", reply_markup=menu_business())
        return
    if data == "menu_setup":
        await query.message.reply_text("📊 ستاپ معامله:", reply_markup=menu_setup())
        return
    if data == "menu_risk":
        await query.message.reply_text("🛡 مدیریت ریسک:", reply_markup=menu_risk())
        return

    if data == "random":
        text = random_message_from_all_categories()
    elif data in MESSAGES:
        text = random.choice(MESSAGES[data])
    else:
        text = "موردی پیدا نشد."

    await query.message.reply_text(text)

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random_message_from_all_categories())

async def reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text="🔁 یادآوری ذهن معامله‌گر:\n\n" + random_message_from_all_categories())

async def repeat_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    context.job_queue.run_repeating(reminder, interval=3600, first=10, chat_id=chat_id, name=str(chat_id))
    await update.message.reply_text("✅ یادآوری هر ۱ ساعت فعال شد.")

async def repeat_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    await update.message.reply_text("⛔ یادآوری متوقف شد.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - منوی اصلی\n/random - پیام تصادفی\n/repeat_on - یادآوری هر ساعت\n/repeat_off - توقف یادآوری")

async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "منوی اصلی"),
        BotCommand("random", "پیام تصادفی"),
        BotCommand("repeat_on", "یادآوری هر ساعت"),
        BotCommand("repeat_off", "توقف یادآوری"),
        BotCommand("help", "راهنما")
    ])

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("repeat_on", repeat_on))
    app.add_handler(CommandHandler("repeat_off", repeat_off))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
