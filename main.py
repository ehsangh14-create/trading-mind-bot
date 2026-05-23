import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MESSAGES = {
    "gold_ui": [
        "🏴‍☠️ گنج بازار\n\nبازار یک گنج عظیم است؛ اما فقط برای کسی که نقشه دارد.\nنقشه تو: روند، کانال، میانگین، حجم، حد زیان و خروج سریع.",
        "🏴‍☠️ قانون گنج\n\nبرای گنج وارد می‌شوم؛ نه برای جنگ.\nسهمم را برمی‌دارم و برمی‌گردم.",
        "🏴‍☠️ جزیره گنج\n\nدر مسیر گنج، طوفان هست، دزد دریایی هست، وسوسه هست.\nاگر از نقشه خارج شوی، گنج به دام تبدیل می‌شود.",
        "🏴‍☠️ کشتی\n\nحساب تو کشتی توست.\nبرای یک سکه، کشتی را غرق نکن.",
        "🏴‍☠️ برداشت از گنج\n\nبازار گنج دارد؛ اما لازم نیست همه گنج امروز برداشته شود.\nیک برداشت درست کافی است."
    ],

    "walmart_ui": [
        "🏪 والمارت خانگی\n\nتو یک والمارت خانگی داری.\nوالمارت هم همه موجودی‌اش را در یک ساعت نمی‌فروشد.",
        "🏪 مغازه حساب\n\nحساب معاملاتی تو مغازه توست.\nدر یک ساعت مغازه را آتش نزن.\nفردا هم مشتری هست.",
        "🏪 بیزینس واقعی\n\nاگر روزی میلیون‌ها دلار گردش معامله داری،\nمثل صاحب یک کسب‌وکار رفتار کن، نه مثل قمارباز عجول.",
        "🏪 اصل فروشگاه\n\nفروشگاه موفق، هر کالا را با برنامه می‌فروشد.\nتریدر موفق، هر معامله را با نقشه انجام می‌دهد.",
        "🏪 حفظ مغازه\n\nهدف اول فروش بیشتر نیست؛\nهدف اول باز ماندن مغازه است."
    ],

    "business_ui": [
        "💼 بیزینس ترید\n\nترید یک بیزینس است.\nهر معامله یک تصمیم مدیریتی است، نه یک هیجان لحظه‌ای.",
        "💼 گردش بزرگ\n\nروزی ۱۰ میلیون دلار می‌توانم معامله کنم؛\nاما نه در یک نقطه، نه در یک قیمت، نه در یک لحظه.",
        "💼 مدیریت\n\nمدیر خوب اول ریسک را کنترل می‌کند، بعد دنبال سود می‌رود.",
        "💼 بقا\n\nاول بقا، بعد سود، بعد رشد حساب.",
        "💼 هدف\n\nهدف، داشتن و نگهداری از حساب است؛\nنه هیجان گرفتن از تعداد معاملات."
    ],

    "capital": [
        "🛡 سرمایه و ریسک\n\nسرمایه من فقط عدد حساب نیست؛\nاعتماد، بقا و ادامه کسب‌وکار من است.",
        "🛡 ریسک\n\nهمه سرمایه را در یک لحظه در معرض ریسک قرار نمی‌دهم.",
        "🛡 حد زیان\n\nحد زیان یعنی: من اشتباه بودن را می‌پذیرم و حسابم را حفظ می‌کنم.",
        "🛡 زیان بزرگ\n\nزیان بزرگ نباید سرمایه را از دست ببرد.\nزیان باید کوچک، کنترل‌شده و قابل پذیرش باشد.",
        "🛡 قانون بقا\n\nحساب زنده بماند، فرصت دوباره هست."
    ],

    "volume": [
        "⚖️ حجم\n\nنه در یک نقطه، نه در یک قیمت، نه در یک لحظه، همه حجم را وارد نکن.",
        "⚖️ تقسیم حجم\n\nاگر قرار است سه لات معامله کنی، آن را در چند نقطه منطقی پخش کن؛ نه با حمله ناگهانی.",
        "⚖️ حجم و بازار\n\nبازار آرام = حجم کمتر\nبازار واضح و قوی = حجم بیشتر",
        "⚖️ ممنوع\n\nهیچ‌وقت به معامله زیان‌ده برای جبران، حجم اضافه نکن.",
        "⚖️ وزن معامله\n\nحجم سنگین با ذهن آشفته، مثل رانندگی با سرعت بالا و بدون ترمز است."
    ],

    "setup": [
        "📊 ستاپ کانال و میانگین\n\n۱. جهت تایم بالا مشخص شود.\n۲. کانال رسم شود.\n۳. میانگین‌ها بررسی شود.\n۴. ورود فقط روی اصلاح.\n۵. حد زیان کوچک.\n۶. خروج سریع.",
        "📊 نقشه معامله\n\nکانال، میانگین، روند، حجم و حد زیان\nنقشه گنج معامله‌اند.",
        "📊 کانال\n\nکف کانال در روند صعودی، محل جستجوی خرید است.\nسقف کانال در روند نزولی، محل جستجوی فروش است.",
        "📊 میانگین‌ها\n\nمیانگین‌ها زبان بازارند.\nقیمت به میانگین‌ها واکنش می‌دهد.\nواکنش را ببین، حدس نزن.",
        "📊 ورود درست\n\nورود خوب باید زود خودش را نشان دهد.\nاگر حرکت نکرد، شاید جای ورود اشتباه بوده."
    ],

    "buy": [
        "📈 خرید حرفه‌ای\n\nدر روند صعودی، روی اصلاح و کف کانال خرید کن؛ نه وسط هیجان شمع بلند.",
        "📈 خرید\n\nدر روند صعودی دنبال کف باش، نه سقف.\nاصلاح، فرصت خرید است.",
        "📈 ممنوع\n\nخرید در سقف ممنوع.\nخرید بعد از شمع بلند هیجانی ممنوع.",
        "📈 خرید آرام\n\nاگر بازار صعودی است، صبر کن تا به ناحیه مناسب برسد.",
        "📈 خرید درست\n\nخرید باید با کانال، میانگین، حد زیان و حجم مناسب همراه باشد."
    ],

    "sell": [
        "📉 فروش حرفه‌ای\n\nدر روند نزولی، روی اصلاح و سقف کانال فروش کن؛ نه بعد از ریزش شدید.",
        "📉 فروش\n\nدر روند نزولی دنبال سقف باش، نه کف.\nاصلاح، فرصت فروش است.",
        "📉 ممنوع\n\nفروش در کف ممنوع.\nفروش بعد از ریزش شدید، اغلب دیر است.",
        "📉 ذهن فروشنده\n\nفروش با خرید فرقی ندارد.\nدر روند نزولی، فروش یعنی همراهی با بازار.",
        "📉 فروش درست\n\nفروش باید با کانال، میانگین، حد زیان و حجم مناسب همراه باشد."
    ],

    "entry_exit": [
        "⚡ ورود و خروج سریع\n\nورود خوب باید سریع وارد سود شود.\nاگر حرکت نکرد، از معامله بیرون بیا یا ریسک را کم کن.",
        "⚡ خروج حرفه‌ای\n\nخروج خوب گاهی مهم‌تر از ورود خوب است.\nسود گرفتی، محافظت کن.",
        "⚡ سود روزانه\n\nسود روزانه را می‌گیرم، چارت را می‌بندم، تا روز بعد.",
        "⚡ بعد از هدف\n\nگل زدی؟ داخل دروازه نمان.\nبعد از رسیدن به هدف، از بازار فاصله بگیر.",
        "⚡ قانون خروج\n\nاگر بازار طبق انتظار حرکت نکرد، آن را به امید و دعا تبدیل نکن؛ خروج کن."
    ],

    "mind": [
        "🧠 ذهن معامله‌گر\n\nذهن به‌راحتی فریب یک شمع بلند را می‌خورد.\nشمع بلند دلیل ورود نیست.",
        "🧠 نرخ موفقیت\n\nنرخ موفقیت مهم است، نه تعداد معاملات.",
        "🧠 ذهن خریدار\n\n۹۵٪ مردم خریدارند؛ اما ۵۰٪ بازار فرصت فروش است.",
        "🧠 فریب ذهن\n\nذهن می‌خواهد دائم در بازار باشد.\nاما بازار کار خودش را می‌کند؛ تو نباید دائم در بازار باشی.",
        "🧠 قانون آرامش\n\nاگر ذهن داغ است، معامله ممنوع.\nاول آرامش، بعد تصمیم."
    ],

    "time": [
        "⏳ زمان\n\nنباید ۲۴ ساعت، ۷ روز هفته معامله کنم.\nبازار همیشه هست؛ انرژی ذهنی من محدود است.",
        "⏳ فردا هم هست\n\nلازم نیست امروز همه چیز را بگیری.\nفردا هم بازار هست. هفته بعد هم هست.",
        "⏳ بعد از سود\n\nسود خوب کردی؟ برو، چند ساعت فاصله بگیر، بعد با ذهن ریست‌شده برگرد.",
        "⏳ سه بار کافی است\n\nسه بار چند معامله کافی است.\nباقی‌اش معمولاً اورترید است.",
        "⏳ صبر\n\nصبر یعنی حفظ سرمایه برای فرصت بهتر."
    ],

    "checklist": [
        "✅ چک‌لیست ورود\n\n۱. جهت تایم بالا مشخص است؟\n۲. کانال رسم شده؟\n۳. میانگین‌ها تایید می‌کنند؟\n۴. ورود روی اصلاح است؟\n۵. حد زیان کوچک است؟\n۶. حجم مناسب است؟",
        "✅ قبل از ورود\n\nآیا ورود از سیستم است یا از فریب شمع بلند؟",
        "✅ قبل از ورود\n\nآیا این معامله حفظ کسب‌وکار است یا تلاش برای جبران؟",
        "✅ قبل از ورود\n\nاگر همین معامله ضرر شود، آیا هنوز حجم و حد زیان منطقی است؟",
        "✅ قبل از ورود\n\nآیا بازار واضح است یا من دارم به زور جهت می‌سازم؟"
    ],

    "quick": [
        "📋 خلاصه سریع\n\nگنج بزرگ است.\nمغازه را حفظ کن.\nحجم را تقسیم کن.\nحد زیان بگذار.\nروی کانال و میانگین وارد شو.\nسود گرفتی، برو.",
        "📋 خلاصه سریع\n\nخرید در سقف ممنوع.\nفروش در کف ممنوع.\nشمع بلند دلیل ورود نیست.\nکانال و میانگین را ببین.",
        "📋 خلاصه سریع\n\nاول بقا.\nبعد سود.\nبعد رشد حساب.",
        "📋 خلاصه سریع\n\nبازار کار خودش را می‌کند.\nتو فقط در جای درست وارد شو و سریع مدیریت کن."
    ]
}


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏴‍☠️ گنج بازار", callback_data="gold_ui"), InlineKeyboardButton("🏪 والمارت خانگی", callback_data="walmart_ui")],
        [InlineKeyboardButton("💼 بیزینس ترید", callback_data="business_ui"), InlineKeyboardButton("🛡 سرمایه و ریسک", callback_data="capital")],
        [InlineKeyboardButton("⚖️ حجم", callback_data="volume"), InlineKeyboardButton("📊 کانال/میانگین", callback_data="setup")],
        [InlineKeyboardButton("📈 خرید حرفه‌ای", callback_data="buy"), InlineKeyboardButton("📉 فروش حرفه‌ای", callback_data="sell")],
        [InlineKeyboardButton("⚡ ورود/خروج سریع", callback_data="entry_exit"), InlineKeyboardButton("🧠 ذهن معامله‌گر", callback_data="mind")],
        [InlineKeyboardButton("⏳ زمان و صبر", callback_data="time"), InlineKeyboardButton("✅ چک‌لیست", callback_data="checklist")],
        [InlineKeyboardButton("📋 خلاصه سریع", callback_data="quick"), InlineKeyboardButton("🎲 پیام تصادفی", callback_data="random")]
    ])


def random_message_from_all_categories():
    all_messages = []
    for items in MESSAGES.values():
        all_messages.extend(items)
    return random.choice(all_messages)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏴‍☠️ گنج بازار | Trading Mind Master\n\n"
        "این ربات برای حفظ حساب، نگاه بیزینسی، ورود درست و خروج سریع ساخته شده.\n\n"
        "UI اصلی:\n"
        "🏴‍☠️ گنج بازار = فرصت عظیم، اما با نقشه\n"
        "🏪 والمارت خانگی = حفظ مغازه و فروش آرام\n"
        "💼 بیزینس ترید = تصمیم مدیریتی، نه هیجان\n\n"
        "یکی از دکمه‌ها را بزن:",
        reply_markup=main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data

    if category == "random":
        text = random_message_from_all_categories()
    elif category in MESSAGES:
        text = random.choice(MESSAGES[category])
    else:
        text = "موردی پیدا نشد."

    await query.message.reply_text(text, reply_markup=main_keyboard())


async def reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    text = random_message_from_all_categories()
    await context.bot.send_message(chat_id=chat_id, text="🔁 یادآوری ذهن معامله‌گر:\n\n" + text)


async def repeat_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    old_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in old_jobs:
        job.schedule_removal()

    context.job_queue.run_repeating(
        reminder,
        interval=3600,
        first=10,
        chat_id=chat_id,
        name=str(chat_id)
    )
    await update.message.reply_text("✅ یادآوری هر ۱ ساعت فعال شد.")


async def repeat_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in jobs:
        job.schedule_removal()
    await update.message.reply_text("⛔ یادآوری متوقف شد.")


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random_message_from_all_categories(), reply_markup=main_keyboard())


async def visual_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖼 نسخه تصویری ربات\n\n"
        "تلگرام می‌تواند عکس، کارت آموزشی، چارت و پنل گرافیکی بفرستد.\n"
        "مرحله بعد می‌توانیم برای هر دکمه یک تصویر ثابت بسازیم:\n\n"
        "🏴‍☠️ کارت گنج بازار\n"
        "🏪 کارت والمارت خانگی\n"
        "📊 کارت ستاپ کانال و میانگین\n"
        "⚡ کارت ورود و خروج سریع",
        reply_markup=main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "دستورها:\n\n"
        "/start - نمایش دکمه‌ها\n"
        "/random - یک پیام تصادفی\n"
        "/visual - توضیح نسخه تصویری\n"
        "/repeat_on - یادآوری هر یک ساعت\n"
        "/repeat_off - توقف یادآوری\n"
        "/help - راهنما"
    )


async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "نمایش دکمه‌ها"),
        BotCommand("random", "پیام تصادفی"),
        BotCommand("visual", "نسخه تصویری"),
        BotCommand("repeat_on", "یادآوری هر یک ساعت"),
        BotCommand("repeat_off", "توقف یادآوری"),
        BotCommand("help", "راهنما"),
    ])


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است. آن را در Railway Variables قرار بده.")

    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("visual", visual_command))
    app.add_handler(CommandHandler("repeat_on", repeat_on))
    app.add_handler(CommandHandler("repeat_off", repeat_off))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
