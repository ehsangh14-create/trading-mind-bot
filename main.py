import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MESSAGES = {
    "mind": [
        "🧠 ذهن\n\nبازار در یک ساعت حساب را نابود نمی‌کند.\nذهنِ بی‌قرار این کار را می‌کند.",
        "🧠 ذهن\n\nترس امروز،\nگاهی خاطره دیروز است،\nنه حقیقت بازار.",
        "🧠 ذهن\n\nذهن می‌خواهد سریع تصمیم بگیرد،\nچون از ندانستن می‌ترسد.",
        "🧠 ذهن\n\nمن اینجا نیستم برای پیش‌بینی.\nمن اینجا هستم برای دیدن.",
        "🧠 ذهن\n\nچارت چیزی نیست.\nقیمت چیزی نیست.\nاین ذهن است که به آن معنا می‌دهد."
    ],
    "greed": [
        "🔥 طمع\n\nحجم بالا،\nفریاد ذهنی‌ست که می‌خواهد\nبازار را مجبور به اطاعت کند.",
        "🔥 طمع\n\nبعد از سود خوب،\nاقیانوس را ترک کن.\nدزدهای دریایی منتظر طمع معامله‌گرند.",
        "🔥 طمع\n\nلازم نیست امروز\nهمه سود دنیا را بگیری.",
        "🔥 طمع\n\nوقتی سود گرفتی و باز هم می‌خواهی بمانی،\nبپرس: سیستم می‌گوید بمانم یا طمع؟"
    ],
    "fear": [
        "😨 ترس\n\nزیان دشمن تو نیست.\nزیان فقط نشان می‌دهد\nکجای مسیر از آگاهی خارج شدی.",
        "😨 ترس\n\nترس یعنی ذهن\nهنوز واقعیت جدید بازار را نپذیرفته.",
        "😨 ترس\n\nاگر حد زیان داری،\nدلیلی برای وحشت نیست.",
        "😨 ترس\n\nاز حد زیان نترس.\nاز معامله بدون حد زیان بترس."
    ],
    "market": [
        "🌊 بازار\n\nبازار مثل اقیانوس است.\nکسی با دست و پا زدن،\nاقیانوس را شکست نداده.",
        "🌊 بازار\n\nبازار استاد بزرگ است.\nبا استاد نباید لج کرد.",
        "🌊 بازار\n\nبازار یا صعودی است،\nیا نزولی،\nیا رنج.\nوظیفه تو جنگیدن نیست؛ فقط دیدن است.",
        "🌊 بازار\n\nاگر بازار نزولی است، بپذیر.\nاگر صعودی است، بپذیر.\nاگر رنج است، بپذیر."
    ],
    "treasure": [
        "🏴‍☠️ جزیره گنج\n\nبازار یک گنج چند صد میلیارد دلاری‌ست.\nباید با احترام وارد شوی،\nبرداری،\nو برگردی.",
        "🏴‍☠️ گنج\n\nبرای گنج رفتی،\nنه برای جنگ.",
        "🏴‍☠️ نقشه گنج\n\nسیستم تو،\nنقشه گنج توست.\nوقتی از نقشه خارج می‌شوی،\nوارد قلمرو ترس و طمع می‌شوی.",
        "🏴‍☠️ کشتی\n\nکسی که برای یک سکه،\nکشتی‌اش را غرق کند،\nهرگز به گنج نمی‌رسد."
    ],
    "business": [
        "🏪 کسب‌وکار\n\nتو شاید روزی\nیک تا سه میلیون دلار معامله انجام بدهی.\nاین چیز کمی نیست.\nاول باید کسب‌وکار را حفظ کرد.",
        "🏪 والمارت خانگی\n\nتو یک والمارت خانگی داری.\nوالمارت هم\nهمه موجودی‌اش را\nدر یک ساعت نمی‌فروشد.",
        "🏪 حفاظت\n\nهدف اول،\nسود کردن نیست.\nهدف اول،\nنابود نکردن حساب است.",
        "🏪 مغازه\n\nحساب معاملاتی تو مغازه توست.\nدر یک ساعت مغازه را آتش نزن.\nفردا هم مشتری هست."
    ],
    "volume": [
        "⚖️ حجم\n\nحجم بالا،\nاغلب تلاش ذهن برای جبران درد است،\nنه بخشی از سیستم.",
        "⚖️ حجم\n\nاگر قرار است سه لات معامله کنی،\nدر چند نقطه وارد شو،\nنه با حمله ناگهانی.",
        "⚖️ حجم\n\nبازار آرام = حجم کمتر\nبازار واضح و قوی = حجم بیشتر",
        "⚖️ حجم\n\nهیچ‌وقت به معامله زیان‌ده\nبرای جبران، حجم اضافه نکن.",
        "⚖️ حجم\n\nحجم زیاد با ذهن آشفته،\nمثل رانندگی با سرعت بالا و بدون ترمز است."
    ],
    "loss": [
        "📉 زیان\n\nبرای جبران یک اشتباه،\nاشتباه بزرگ‌تر نکن.",
        "📉 زیان\n\nزیان را کوچک ببند.\nحساب زنده بماند، فرصت دوباره هست.",
        "📉 زیان\n\nاگر امروز زیان کردی،\nلازم نیست همین امروز انتقام بگیری.",
        "📉 زیان\n\nاضافه کردن حجم به معامله زیان‌ده،\nخاموش کردن آتش با بنزین است."
    ],
    "profit": [
        "📈 سود\n\nسود خوب کردی؟\nچارت را ببند.\nبرگرد به زندگی.",
        "📈 سود\n\nسود را محافظت کن.\nبازار چیزی به کسی بدهکار نیست.",
        "📈 سود\n\nبعد از سود،\nمغرور نشو.\nبازار فردا دوباره امتحان می‌گیرد.",
        "📈 سود\n\nاگر سود راحت آمد،\nاحتمالاً هم‌جهت جریان بودی.\nبه زور سود نگیر."
    ],
    "freedom": [
        "🕊 رهایی\n\nچارت فقط موج است.\nتو موج نیستی.",
        "🕊 رهایی\n\nبازار را هل نده.\nموج خودش حرکت می‌کند.",
        "🕊 رهایی\n\nدیدن.\nپذیرفتن.\nعمل.\nرها کردن.",
        "🕊 رهایی\n\nمن کنترل بازار را ندارم.\nمن فقط کنترل رفتار خودم را دارم."
    ],
    "time": [
        "⏳ زمان\n\nفردا هم بازار هست.\nهفته بعد هم هست.\nسال بعد هم هست.",
        "⏳ صبر\n\nلازم نیست امروز\nهمه چیز را بگیری.",
        "⏳ آرامش\n\nوقتی سود خوبی گرفتی،\nچارت را ببند.\nبرگرد به زندگی.",
        "⏳ فرصت\n\nبازار کمبود ندارد.\nتنها چیزی که کم می‌شود،\nآرامش معامله‌گر عجول است."
    ],
    "checklist": [
        "✅ چک‌لیست ورود\n\n۱. جهت بازار چیست؟\n۲. حجم مناسب است؟\n۳. حد زیان مشخص است؟\n۴. خبر مهم نزدیک نیست؟\n۵. ورود از سیستم است یا احساس؟",
        "✅ قبل از ورود\n\nآیا دارم می‌بینم؟\nیا فقط می‌خواهم حق با من باشد؟",
        "✅ قبل از ورود\n\nاگر همین معامله ضرر شود،\nآیا هنوز حجم و حد زیان منطقی است؟",
        "✅ قبل از ورود\n\nآیا این معامله،\nحفظ کسب‌وکار است\nیا قمار برای جبران؟"
    ]
}

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 ذهن", callback_data="mind"), InlineKeyboardButton("🔥 طمع", callback_data="greed")],
        [InlineKeyboardButton("😨 ترس", callback_data="fear"), InlineKeyboardButton("🌊 بازار", callback_data="market")],
        [InlineKeyboardButton("🏴‍☠️ گنج", callback_data="treasure"), InlineKeyboardButton("🏪 کسب‌وکار", callback_data="business")],
        [InlineKeyboardButton("⚖️ حجم", callback_data="volume"), InlineKeyboardButton("📉 زیان", callback_data="loss")],
        [InlineKeyboardButton("📈 سود", callback_data="profit"), InlineKeyboardButton("🕊 رهایی", callback_data="freedom")],
        [InlineKeyboardButton("⏳ زمان", callback_data="time"), InlineKeyboardButton("✅ چک‌لیست", callback_data="checklist")]
    ])

def random_message_from_all_categories():
    all_messages = []
    for items in MESSAGES.values():
        all_messages.extend(items)
    return random.choice(all_messages)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n\nاین ربات، مرشد ذهن معامله‌گر است.\nبرای یادآوری، یکی از دکمه‌ها را بزن:",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data
    text = random.choice(MESSAGES[category]) if category in MESSAGES else "موردی پیدا نشد."
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "دستورها:\n\n"
        "/start - نمایش دکمه‌ها\n"
        "/repeat_on - فعال کردن یادآوری هر یک ساعت\n"
        "/repeat_off - توقف یادآوری\n\n"
        "هر دکمه را بزنی، یک پیام تصادفی از همان بخش می‌آید."
    )

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است. آن را در Railway Variables قرار بده.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("repeat_on", repeat_on))
    app.add_handler(CommandHandler("repeat_off", repeat_off))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
