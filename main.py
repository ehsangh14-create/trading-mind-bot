import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8914364157:AAHsKiFwyEqc_Hkc3Wwiguw19ZM8cat9If0"

MESSAGES = {
    "volume": "📊 حجم معامله:\nقبل از ورود بپرس: اگر ضرر کنم، آیا این حجم هنوز منطقی است؟\nحجم زیاد = نابودی آرام سرمایه.",
    "market": "🌍 وضعیت بازار:\nاول بازار را بخوان، بعد معامله کن.\nروند؟ رنج؟ خبر مهم؟ نقدینگی؟ عجله ممنوع.",
    "sl_tp": "🎯 حد ضرر و سود:\nقبل از ورود باید SL و TP مشخص باشد.\nمعامله بدون حد ضرر یعنی امید، نه سیستم.",
    "emotion": "🧠 احساسات:\nاگر عصبانی، هیجان‌زده یا انتقام‌جو هستی، معامله نکن.\nبازار منتظر آرام‌هاست.",
    "checklist": "✅ چک‌لیست ورود:\n1. روند مشخص؟\n2. خبر مهم نیست؟\n3. حجم مناسب؟\n4. SL مشخص؟\n5. نسبت سود به زیان منطقی؟"
}

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 حجم", callback_data="volume"),
            InlineKeyboardButton("🌍 بازار", callback_data="market"),
        ],
        [
            InlineKeyboardButton("🎯 حد ضرر/سود", callback_data="sl_tp"),
            InlineKeyboardButton("🧠 احساسات", callback_data="emotion"),
        ],
        [
            InlineKeyboardButton("✅ چک‌لیست ورود", callback_data="checklist"),
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nاین ربات برای تکرار اصول مهم ترید ساخته شده.\nیکی از دکمه‌ها را بزن:",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = MESSAGES.get(query.data, "موردی پیدا نشد.")
    await query.message.reply_text(text, reply_markup=main_keyboard())

async def reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    text = random.choice(list(MESSAGES.values()))
    await context.bot.send_message(chat_id=chat_id, text="🔁 یادآوری ترید:\n\n" + text)

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

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("repeat_on", repeat_on))
    app.add_handler(CommandHandler("repeat_off", repeat_off))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
