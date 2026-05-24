import os
import json
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TZ = ZoneInfo("America/Vancouver")

CONFIG_FILE = "life_config.json"
DATA_FILE = "life_data.json"
NOTES_FILE = "notes.json"
REMINDERS_FILE = "reminders.json"
USER_STATE_FILE = "user_state.json"

DEFAULT_CONFIG = {
    "study": {
        "title": "📚 مطالعه",
        "subjects": {
            "cpa": {"title": "CPA", "subs": {"fr": "Financial Reporting / مالی", "tax": "Taxation / مالیات", "audit": "Audit / حسابرسی", "mgmt": "Management / مدیریت"}},
            "english": {"title": "English / انگلیسی", "subs": {"grammar": "Grammar", "speaking": "Speaking", "listening": "Listening", "vocab": "Vocabulary"}},
            "python": {"title": "Python / پایتون", "subs": {"basic": "Basics", "finance": "Finance Analysis", "bot": "Telegram Bot"}}
        }
    },
    "trading": {
        "title": "📊 ترید عملی",
        "subjects": {
            "xauusd": {"title": "XAUUSD / طلا", "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}},
            "eurusd": {"title": "EURUSD", "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}},
            "usdjpy": {"title": "USDJPY", "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}},
            "nasdaq": {"title": "NASDAQ", "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}},
            "btc": {"title": "BTC / کریپتو", "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}}
        }
    },
    "uber": {"title": "🚗 اوبر", "subjects": {"drive": {"title": "Driving / رانندگی", "subs": {"work": "Work Shift", "airport": "Airport", "city": "City"}}}},
    "walk": {"title": "🚶 پیاده‌روی", "subjects": {"walk": {"title": "Walking", "subs": {"normal": "Normal Walk", "fast": "Fast Walk", "family": "Family Walk"}}}},
    "sleep": {"title": "😴 خواب", "subjects": {"sleep": {"title": "Sleep", "subs": {"night": "Night Sleep", "nap": "Nap"}}}},
    "misc": {
        "title": "🧩 متفرقه",
        "subjects": {
            "shopping": {"title": "🛒 خرید", "subs": {"grocery": "خرید خانه", "personal": "خرید شخصی", "car": "خرید ماشین/ابزار"}},
            "errands": {"title": "📌 کارهای بیرون", "subs": {"bank": "بانک", "school": "مدرسه", "appointment": "قرار/ملاقات"}},
            "home": {"title": "🏠 خانه", "subs": {"clean": "نظافت", "repair": "تعمیرات", "family": "خانواده"}}
        }
    }
}

MIND_MESSAGES = {
    "mind": [
        "🧠 فریب ذهن\n\nذهن می‌خواهد دائم در بازار باشد؛ اما بازار کار خودش را می‌کند. تو نباید دائم در بازار باشی.",
        "🧠 شمع بلند\n\nذهن به‌راحتی فریب یک شمع بلند را می‌خورد. شمع بلند دلیل ورود نیست."
    ],
    "business": [
        "🏪 والمارت خانگی\n\nتو یک والمارت خانگی داری. والمارت هم همه موجودی‌اش را در یک ساعت نمی‌فروشد.",
        "🏴‍☠️ گنج بازار\n\nبرای گنج وارد می‌شوم؛ نه برای جنگ. سهمم را برمی‌دارم و برمی‌گردم."
    ],
    "setup": [
        "📊 ستاپ\n\nجهت تایم بالا، کانال، میانگین، اصلاح، حد زیان کوچک، خروج سریع."
    ],
    "risk": [
        "⚖️ حجم\n\nنه در یک نقطه، نه در یک قیمت، نه در یک لحظه، همه حجم را وارد نکن.",
        "🛑 حد زیان\n\nحد زیان یعنی: من اشتباه بودن را می‌پذیرم و حسابم را حفظ می‌کنم."
    ]
}

def now():
    return datetime.now(TZ)

def now_iso():
    return now().isoformat(timespec="seconds")

def parse_dt(s):
    return datetime.fromisoformat(s)

def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default)
        return json.loads(json.dumps(default, ensure_ascii=False))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return json.loads(json.dumps(default, ensure_ascii=False))

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config():
    return load_json(CONFIG_FILE, DEFAULT_CONFIG)

def save_config(data):
    save_json(CONFIG_FILE, data)

def load_data():
    return load_json(DATA_FILE, {"active": {}, "sessions": []})

def save_data(data):
    save_json(DATA_FILE, data)

def load_notes():
    return load_json(NOTES_FILE, [])

def save_notes(data):
    save_json(NOTES_FILE, data)

def load_reminders():
    return load_json(REMINDERS_FILE, [])

def save_reminders(data):
    save_json(REMINDERS_FILE, data)

def load_states():
    return load_json(USER_STATE_FILE, {})

def save_states(data):
    save_json(USER_STATE_FILE, data)

def safe_key(text):
    base = text.strip().lower().replace(" ", "_").replace("/", "_").replace(":", "_")
    base = "".join(ch for ch in base if ch.isalnum() or ch in "_-")
    return base[:30] or f"item_{int(now().timestamp())}"

def fmt_duration(seconds):
    minutes = int(float(seconds) // 60)
    h = minutes // 60
    m = minutes % 60
    if h and m:
        return f"{h} ساعت و {m} دقیقه"
    if h:
        return f"{h} ساعت"
    return f"{m} دقیقه"

def set_pending(user_id, action, payload):
    states = load_states()
    states[str(user_id)] = {"action": action, "payload": payload}
    save_states(states)

def pop_pending(user_id):
    states = load_states()
    state = states.pop(str(user_id), None)
    save_states(states)
    return state

def root_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏴‍☠️ Trading Mind Master", callback_data="root:mind")],
        [InlineKeyboardButton("🧠 Personal Life OS", callback_data="root:life")]
    ])

def mind_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 ذهن", callback_data="mind:mind"), InlineKeyboardButton("🏪 بیزینس", callback_data="mind:business")],
        [InlineKeyboardButton("📊 ستاپ", callback_data="mind:setup"), InlineKeyboardButton("🛡 ریسک", callback_data="mind:risk")],
        [InlineKeyboardButton("🎲 پیام تصادفی", callback_data="mind:random")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="root")]
    ])

def life_menu():
    cfg = load_config()
    rows = []
    for k, v in cfg.items():
        rows.append([InlineKeyboardButton(v["title"], callback_data=f"act:{k}")])
    rows.append([InlineKeyboardButton("📊 گزارش امروز", callback_data="report:today"), InlineKeyboardButton("⏹ پایان فعال", callback_data="stop:active")])
    rows.append([InlineKeyboardButton("⏰ ریمایندر", callback_data="reminder:menu"), InlineKeyboardButton("📝 یادداشت‌ها", callback_data="notes:list")])
    rows.append([InlineKeyboardButton("➕ افزودن بخش اصلی", callback_data="add:activity"), InlineKeyboardButton("⚙️ مدیریت بخش‌ها", callback_data="manage:activities")])
    rows.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="root")])
    return InlineKeyboardMarkup(rows)

def subject_menu(activity):
    cfg = load_config()
    rows = []
    for sk, sv in cfg[activity]["subjects"].items():
        rows.append([InlineKeyboardButton(sv["title"], callback_data=f"subj:{activity}:{sk}")])
    if activity == "trading":
        rows.append([InlineKeyboardButton("➕ افزودن نماد", callback_data="add:trading_symbol")])
    rows.append([InlineKeyboardButton("➕ افزودن موضوع", callback_data=f"add:subject:{activity}"), InlineKeyboardButton("⚙️ مدیریت موضوع‌ها", callback_data=f"manage:subjects:{activity}")])
    rows.append([InlineKeyboardButton("✏️ ویرایش این بخش", callback_data=f"edit:activity:{activity}"), InlineKeyboardButton("🗑 حذف این بخش", callback_data=f"delete_confirm:activity:{activity}")])
    rows.append([InlineKeyboardButton("📝 یادداشت برای این بخش", callback_data=f"note:activity:{activity}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data="root:life")])
    return InlineKeyboardMarkup(rows)

def sub_menu(activity, subject):
    cfg = load_config()
    rows = []
    for subk, subv in cfg[activity]["subjects"][subject]["subs"].items():
        rows.append([InlineKeyboardButton(subv, callback_data=f"item:{activity}:{subject}:{subk}")])
    rows.append([InlineKeyboardButton("➕ افزودن زیرموضوع", callback_data=f"add:sub:{activity}:{subject}"), InlineKeyboardButton("⚙️ مدیریت زیرموضوع‌ها", callback_data=f"manage:subs:{activity}:{subject}")])
    rows.append([InlineKeyboardButton("✏️ ویرایش موضوع", callback_data=f"edit:subject:{activity}:{subject}"), InlineKeyboardButton("🗑 حذف موضوع", callback_data=f"delete_confirm:subject:{activity}:{subject}")])
    rows.append([InlineKeyboardButton("📝 یادداشت برای این موضوع", callback_data=f"note:subject:{activity}:{subject}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data=f"act:{activity}")])
    return InlineKeyboardMarkup(rows)

def item_menu(activity, subject, sub):
    cfg = load_config()
    title = cfg[activity]["subjects"][subject]["subs"][sub]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ شروع", callback_data=f"startsession:{activity}:{subject}:{sub}")],
        [InlineKeyboardButton("✏️ ویرایش زیرموضوع", callback_data=f"edit:sub:{activity}:{subject}:{sub}"), InlineKeyboardButton("🗑 حذف زیرموضوع", callback_data=f"delete_confirm:sub:{activity}:{subject}:{sub}")],
        [InlineKeyboardButton("📝 یادداشت برای این مورد", callback_data=f"note:item:{activity}:{subject}:{sub}")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data=f"subj:{activity}:{subject}")]
    ])

def manage_activities_menu():
    cfg = load_config()
    rows = []
    for k, v in cfg.items():
        rows.append([InlineKeyboardButton("✏️ " + v["title"], callback_data=f"edit:activity:{k}"),
                     InlineKeyboardButton("🗑", callback_data=f"delete_confirm:activity:{k}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data="root:life")])
    return InlineKeyboardMarkup(rows)

def manage_subjects_menu(activity):
    cfg = load_config()
    rows = []
    for sk, sv in cfg[activity]["subjects"].items():
        rows.append([InlineKeyboardButton("✏️ " + sv["title"], callback_data=f"edit:subject:{activity}:{sk}"),
                     InlineKeyboardButton("🗑", callback_data=f"delete_confirm:subject:{activity}:{sk}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data=f"act:{activity}")])
    return InlineKeyboardMarkup(rows)

def manage_subs_menu(activity, subject):
    cfg = load_config()
    rows = []
    for subk, subv in cfg[activity]["subjects"][subject]["subs"].items():
        rows.append([InlineKeyboardButton("✏️ " + subv, callback_data=f"edit:sub:{activity}:{subject}:{subk}"),
                     InlineKeyboardButton("🗑", callback_data=f"delete_confirm:sub:{activity}:{subject}:{subk}")])
    rows.append([InlineKeyboardButton("⬅️ برگشت", callback_data=f"subj:{activity}:{subject}")])
    return InlineKeyboardMarkup(rows)

def delete_confirm_menu(kind, parts):
    data = "delete:" + kind + ":" + ":".join(parts)
    back = "root:life"
    if kind == "activity":
        back = f"act:{parts[0]}"
    elif kind == "subject":
        back = f"subj:{parts[0]}:{parts[1]}"
    elif kind == "sub":
        back = f"item:{parts[0]}:{parts[1]}:{parts[2]}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ بله، حذف کن", callback_data=data)],
        [InlineKeyboardButton("❌ انصراف", callback_data=back)]
    ])

def reminder_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 تاریخ مشخص", callback_data="reminder:add_once")],
        [InlineKeyboardButton("🔁 روزانه", callback_data="reminder:add_daily")],
        [InlineKeyboardButton("📆 هفتگی", callback_data="reminder:add_weekly")],
        [InlineKeyboardButton("🗓 ماهانه", callback_data="reminder:add_monthly")],
        [InlineKeyboardButton("📋 لیست ریمایندرها", callback_data="reminder:list")],
        [InlineKeyboardButton("⬅️ برگشت", callback_data="root:life")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سیستم اصلی:", reply_markup=root_menu())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = pop_pending(user_id)
    if not state:
        await update.message.reply_text("برای شروع از /start استفاده کن.")
        return

    action = state["action"]
    payload = state["payload"]
    cfg = load_config()

    if action == "add_activity":
        key = safe_key(text)
        cfg[key] = {"title": text, "subjects": {"default": {"title": "عمومی", "subs": {"general": "عمومی"}}}}
        save_config(cfg)
        await update.message.reply_text(f"✅ بخش اصلی اضافه شد: {text}", reply_markup=life_menu())
    elif action == "add_subject":
        activity = payload["activity"]
        key = safe_key(text)
        cfg[activity]["subjects"][key] = {"title": text, "subs": {"general": "عمومی"}}
        save_config(cfg)
        await update.message.reply_text(f"✅ موضوع اضافه شد: {text}", reply_markup=subject_menu(activity))
    elif action == "add_sub":
        activity = payload["activity"]; subject = payload["subject"]
        key = safe_key(text)
        cfg[activity]["subjects"][subject]["subs"][key] = text
        save_config(cfg)
        await update.message.reply_text(f"✅ زیرموضوع اضافه شد: {text}", reply_markup=sub_menu(activity, subject))
    elif action == "add_trading_symbol":
        key = safe_key(text.upper())
        cfg["trading"]["subjects"][key] = {"title": text.upper(), "subs": {"analysis": "تحلیل", "live": "معامله زنده", "journal": "ژورنال معامله", "backtest": "بک‌تست"}}
        save_config(cfg)
        await update.message.reply_text(f"✅ نماد اضافه شد: {text.upper()}", reply_markup=subject_menu("trading"))
    elif action == "edit_activity":
        activity = payload["activity"]
        cfg[activity]["title"] = text
        save_config(cfg)
        await update.message.reply_text("✅ نام بخش ویرایش شد.", reply_markup=subject_menu(activity))
    elif action == "edit_subject":
        activity = payload["activity"]; subject = payload["subject"]
        cfg[activity]["subjects"][subject]["title"] = text
        save_config(cfg)
        await update.message.reply_text("✅ نام موضوع ویرایش شد.", reply_markup=sub_menu(activity, subject))
    elif action == "edit_sub":
        activity = payload["activity"]; subject = payload["subject"]; sub = payload["sub"]
        cfg[activity]["subjects"][subject]["subs"][sub] = text
        save_config(cfg)
        await update.message.reply_text("✅ نام زیرموضوع ویرایش شد.", reply_markup=item_menu(activity, subject, sub))
    elif action.startswith("note_"):
        notes = load_notes()
        notes.append({"time": now_iso(), "type": action, "payload": payload, "text": text})
        save_notes(notes)
        await update.message.reply_text("✅ یادداشت ثبت شد.", reply_markup=life_menu())
    elif action == "reminder":
        try:
            rem = create_reminder_from_text(payload["type"], text, update.effective_chat.id)
        except Exception:
            await update.message.reply_text("فرمت درست نبود.\n\n" + reminder_help(payload["type"]))
            return
        reminders = load_reminders()
        reminders.append(rem)
        save_reminders(reminders)
        await update.message.reply_text("✅ ریمایندر ثبت شد.", reply_markup=reminder_menu())

def reminder_help(rtype):
    if rtype == "once":
        return "مثال:\n2026-06-20 09:30 پرداخت بیمه"
    if rtype == "daily":
        return "مثال:\n21:00 ژورنال شب"
    if rtype == "weekly":
        return "مثال:\nMON 09:00 گزارش هفتگی\nروزها: MON TUE WED THU FRI SAT SUN"
    if rtype == "monthly":
        return "مثال:\n1 09:00 پرداخت اجاره"
    return ""

def create_reminder_from_text(rtype, text, chat_id):
    parts = text.split()
    if rtype == "once":
        dt = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        return {"id": str(int(now().timestamp()*1000)), "chat_id": chat_id, "type": "once", "message": " ".join(parts[2:]), "next_time": dt.isoformat(timespec="seconds")}
    if rtype == "daily":
        h, m = map(int, parts[0].split(":"))
        nxt = now().replace(hour=h, minute=m, second=0, microsecond=0)
        if nxt <= now():
            nxt += timedelta(days=1)
        return {"id": str(int(now().timestamp()*1000)), "chat_id": chat_id, "type": "daily", "message": " ".join(parts[1:]), "time": parts[0], "next_time": nxt.isoformat(timespec="seconds")}
    if rtype == "weekly":
        days = {"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5,"SUN":6}
        day = parts[0].upper()
        h, m = map(int, parts[1].split(":"))
        delta = (days[day] - now().weekday()) % 7
        nxt = now().replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(days=delta)
        if nxt <= now():
            nxt += timedelta(days=7)
        return {"id": str(int(now().timestamp()*1000)), "chat_id": chat_id, "type": "weekly", "message": " ".join(parts[2:]), "day": day, "time": parts[1], "next_time": nxt.isoformat(timespec="seconds")}
    if rtype == "monthly":
        day = int(parts[0])
        h, m = map(int, parts[1].split(":"))
        t = now()
        month, year = t.month, t.year
        while True:
            try:
                nxt = t.replace(year=year, month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
                if nxt > t:
                    break
            except ValueError:
                pass
            month += 1
            if month == 13:
                month = 1
                year += 1
        return {"id": str(int(now().timestamp()*1000)), "chat_id": chat_id, "type": "monthly", "message": " ".join(parts[2:]), "day": day, "time": parts[1], "next_time": nxt.isoformat(timespec="seconds")}
    raise ValueError("bad reminder")

def advance_reminder(rem):
    current = parse_dt(rem["next_time"])
    if rem["type"] == "once":
        rem["done"] = True
    elif rem["type"] == "daily":
        rem["next_time"] = (current + timedelta(days=1)).isoformat(timespec="seconds")
    elif rem["type"] == "weekly":
        rem["next_time"] = (current + timedelta(days=7)).isoformat(timespec="seconds")
    elif rem["type"] == "monthly":
        month = current.month + 1
        year = current.year
        if month == 13:
            month = 1
            year += 1
        day = rem["day"]
        h, m = map(int, rem["time"].split(":"))
        while True:
            try:
                nxt = current.replace(year=year, month=month, day=day, hour=h, minute=m, second=0, microsecond=0)
                break
            except ValueError:
                month += 1
                if month == 13:
                    month = 1
                    year += 1
        rem["next_time"] = nxt.isoformat(timespec="seconds")

async def reminder_checker(context: ContextTypes.DEFAULT_TYPE):
    reminders = load_reminders()
    changed = False
    for rem in reminders:
        if rem.get("done"):
            continue
        if parse_dt(rem["next_time"]) <= now():
            await context.bot.send_message(chat_id=rem["chat_id"], text="⏰ یادآوری:\n\n" + rem["message"])
            advance_reminder(rem)
            changed = True
    if changed:
        save_reminders([r for r in reminders if not r.get("done")])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    cfg = load_config()

    if data == "root":
        await q.message.reply_text("سیستم اصلی:", reply_markup=root_menu()); return
    if data == "root:mind":
        await q.message.reply_text("🏴‍☠️ Trading Mind Master:", reply_markup=mind_menu()); return
    if data == "root:life":
        await q.message.reply_text("🧠 Personal Life OS:", reply_markup=life_menu()); return

    if data.startswith("mind:"):
        key = data.split(":")[1]
        if key == "random":
            allm = [m for arr in MIND_MESSAGES.values() for m in arr]
            await q.message.reply_text(random.choice(allm), reply_markup=mind_menu())
        else:
            await q.message.reply_text(random.choice(MIND_MESSAGES[key]), reply_markup=mind_menu())
        return

    if data.startswith("act:"):
        activity = data.split(":")[1]
        await q.message.reply_text(f"{cfg[activity]['title']}\nموضوع را انتخاب کن:", reply_markup=subject_menu(activity)); return

    if data.startswith("subj:"):
        _, activity, subject = data.split(":")
        await q.message.reply_text("زیرموضوع را انتخاب کن:", reply_markup=sub_menu(activity, subject)); return

    if data.startswith("item:"):
        _, activity, subject, sub = data.split(":")
        title = cfg[activity]["subjects"][subject]["subs"][sub]
        await q.message.reply_text(f"انتخاب شد:\n{title}", reply_markup=item_menu(activity, subject, sub)); return

    if data.startswith("startsession:"):
        _, activity, subject, sub = data.split(":")
        user_id = str(q.from_user.id)
        store = load_data()
        if user_id in store["active"]:
            a = store["active"][user_id]
            await q.message.reply_text(f"⚠️ یک فعالیت فعال داری:\n{a['activity_title']} / {a['subject_title']} / {a['sub_title']}", reply_markup=life_menu()); return
        start_time = now_iso()
        active = {"activity": activity, "subject": subject, "sub": sub, "activity_title": cfg[activity]["title"], "subject_title": cfg[activity]["subjects"][subject]["title"], "sub_title": cfg[activity]["subjects"][subject]["subs"][sub], "start_time": start_time}
        store["active"][user_id] = active
        save_data(store)
        await q.message.reply_text(f"▶️ شروع شد:\n{active['activity_title']} / {active['subject_title']} / {active['sub_title']}\n{parse_dt(start_time).strftime('%Y-%m-%d %H:%M')}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹ پایان", callback_data="stop:active")],[InlineKeyboardButton("🏠 Life OS", callback_data="root:life")]])); return

    if data == "stop:active":
        user_id = str(q.from_user.id)
        store = load_data()
        if user_id not in store["active"]:
            await q.message.reply_text("فعالیت فعالی وجود ندارد.", reply_markup=life_menu()); return
        active = store["active"].pop(user_id)
        end_time = now_iso()
        st, en = parse_dt(active["start_time"]), parse_dt(end_time)
        dur = (en - st).total_seconds()
        session = dict(active)
        session.update({"end_time": end_time, "duration_seconds": dur, "date": st.strftime("%Y-%m-%d")})
        store["sessions"].append(session)
        save_data(store)
        await q.message.reply_text(f"⏹ پایان یافت:\n{active['activity_title']} / {active['subject_title']} / {active['sub_title']}\nمدت: {fmt_duration(dur)}", reply_markup=life_menu()); return

    if data.startswith("add:"):
        parts = data.split(":")
        if parts[1] == "activity":
            set_pending(q.from_user.id, "add_activity", {})
            await q.message.reply_text("نام بخش اصلی جدید را بنویس:")
        elif parts[1] == "subject":
            set_pending(q.from_user.id, "add_subject", {"activity": parts[2]})
            await q.message.reply_text("نام موضوع جدید را بنویس:")
        elif parts[1] == "sub":
            set_pending(q.from_user.id, "add_sub", {"activity": parts[2], "subject": parts[3]})
            await q.message.reply_text("نام زیرموضوع جدید را بنویس:")
        elif parts[1] == "trading_symbol":
            set_pending(q.from_user.id, "add_trading_symbol", {})
            await q.message.reply_text("نماد جدید را بنویس. مثال: GBPJPY")
        return

    if data.startswith("edit:"):
        parts = data.split(":")
        if parts[1] == "activity":
            set_pending(q.from_user.id, "edit_activity", {"activity": parts[2]})
            await q.message.reply_text("نام جدید بخش را بنویس:")
        elif parts[1] == "subject":
            set_pending(q.from_user.id, "edit_subject", {"activity": parts[2], "subject": parts[3]})
            await q.message.reply_text("نام جدید موضوع را بنویس:")
        elif parts[1] == "sub":
            set_pending(q.from_user.id, "edit_sub", {"activity": parts[2], "subject": parts[3], "sub": parts[4]})
            await q.message.reply_text("نام جدید زیرموضوع را بنویس:")
        return

    if data.startswith("delete_confirm:"):
        parts = data.split(":")
        await q.message.reply_text("⚠️ مطمئنی می‌خواهی حذف کنی؟\nاین کار قابل برگشت نیست.", reply_markup=delete_confirm_menu(parts[1], parts[2:])); return

    if data.startswith("delete:"):
        parts = data.split(":")
        kind = parts[1]
        if kind == "activity":
            cfg.pop(parts[2], None); save_config(cfg)
            await q.message.reply_text("✅ بخش حذف شد.", reply_markup=life_menu())
        elif kind == "subject":
            cfg[parts[2]]["subjects"].pop(parts[3], None); save_config(cfg)
            await q.message.reply_text("✅ موضوع حذف شد.", reply_markup=subject_menu(parts[2]))
        elif kind == "sub":
            cfg[parts[2]]["subjects"][parts[3]]["subs"].pop(parts[4], None); save_config(cfg)
            await q.message.reply_text("✅ زیرموضوع حذف شد.", reply_markup=sub_menu(parts[2], parts[3]))
        return

    if data.startswith("manage:"):
        parts = data.split(":")
        if parts[1] == "activities":
            await q.message.reply_text("⚙️ مدیریت بخش‌ها:", reply_markup=manage_activities_menu())
        elif parts[1] == "subjects":
            await q.message.reply_text("⚙️ مدیریت موضوع‌ها:", reply_markup=manage_subjects_menu(parts[2]))
        elif parts[1] == "subs":
            await q.message.reply_text("⚙️ مدیریت زیرموضوع‌ها:", reply_markup=manage_subs_menu(parts[2], parts[3]))
        return

    if data.startswith("note:"):
        parts = data.split(":")
        set_pending(q.from_user.id, "note_" + parts[1], {"parts": parts[2:]})
        await q.message.reply_text("یادداشتت را بنویس:"); return

    if data == "notes:list":
        notes = load_notes()[-10:]
        if not notes:
            await q.message.reply_text("یادداشتی ثبت نشده.", reply_markup=life_menu())
        else:
            lines = ["📝 آخرین یادداشت‌ها:\n"] + [f"• {n['time'][:16]} - {n['text']}" for n in notes]
            await q.message.reply_text("\n".join(lines), reply_markup=life_menu())
        return

    if data == "report:today":
        await send_today_report(q.message); return

    if data == "reminder:menu":
        await q.message.reply_text("⏰ ریمایندر:", reply_markup=reminder_menu()); return
    if data.startswith("reminder:add_"):
        rtype = data.replace("reminder:add_", "")
        set_pending(q.from_user.id, "reminder", {"type": rtype})
        await q.message.reply_text(reminder_help(rtype)); return
    if data == "reminder:list":
        reminders = load_reminders()
        if not reminders:
            await q.message.reply_text("ریمایندری ثبت نشده.", reply_markup=reminder_menu())
        else:
            lines = ["📋 ریمایندرها:\n"] + [f"• {r['type']} | {r['next_time'][:16]} | {r['message']}" for r in reminders[-15:]]
            await q.message.reply_text("\n".join(lines), reply_markup=reminder_menu())
        return

async def send_today_report(message):
    today = now().strftime("%Y-%m-%d")
    store = load_data()
    sessions = [s for s in store["sessions"] if s.get("date") == today]
    if not sessions:
        await message.reply_text("برای امروز هنوز فعالیتی ثبت نشده.", reply_markup=life_menu()); return
    totals = {}
    for s in sessions:
        key = f"{s['activity_title']} / {s['subject_title']} / {s['sub_title']}"
        totals[key] = totals.get(key, 0) + float(s["duration_seconds"])
    lines = [f"📊 گزارش امروز - {today}\n"] + [f"• {k}: {fmt_duration(sec)}" for k, sec in totals.items()]
    await message.reply_text("\n".join(lines), reply_markup=life_menu())

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_today_report(update.message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - منوی اصلی\n/today - گزارش امروز\n/help - راهنما")

async def post_init(app: Application):
    await app.bot.set_my_commands([BotCommand("start", "منوی اصلی"), BotCommand("today", "گزارش امروز"), BotCommand("help", "راهنما")])
    app.job_queue.run_repeating(reminder_checker, interval=60, first=10)

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Enhanced Combined Bot with Edit/Delete is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
