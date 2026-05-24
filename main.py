import os, json, random
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
STATE_FILE = "user_state.json"

DEFAULT_CONFIG = {
    "study": {"title":"📚 مطالعه","subjects":{
        "cpa":{"title":"CPA","subs":{"fr":"Financial Reporting / مالی","tax":"Taxation / مالیات","audit":"Audit / حسابرسی","mgmt":"Management / مدیریت"}},
        "english":{"title":"English / انگلیسی","subs":{"grammar":"Grammar","speaking":"Speaking","listening":"Listening","vocab":"Vocabulary"}},
        "python":{"title":"Python / پایتون","subs":{"basic":"Basics","finance":"Finance Analysis","bot":"Telegram Bot"}}
    }},
    "trading": {"title":"📊 ترید عملی","subjects":{
        "xauusd":{"title":"XAUUSD / طلا","subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}},
        "eurusd":{"title":"EURUSD","subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}},
        "usdjpy":{"title":"USDJPY","subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}},
        "nasdaq":{"title":"NASDAQ","subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}},
        "btc":{"title":"BTC / کریپتو","subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}}
    }},
    "uber":{"title":"🚗 اوبر","subjects":{"drive":{"title":"Driving / رانندگی","subs":{"work":"Work Shift","airport":"Airport","city":"City"}}}},
    "walk":{"title":"🚶 پیاده‌روی","subjects":{"walk":{"title":"Walking","subs":{"normal":"Normal Walk","fast":"Fast Walk","family":"Family Walk"}}}},
    "sleep":{"title":"😴 خواب","subjects":{"sleep":{"title":"Sleep","subs":{"night":"Night Sleep","nap":"Nap"}}}},
    "misc":{"title":"🧩 متفرقه","subjects":{
        "shopping":{"title":"🛒 خرید","subs":{"grocery":"خرید خانه","personal":"خرید شخصی","car":"خرید ماشین/ابزار"}},
        "errands":{"title":"📌 کارهای بیرون","subs":{"bank":"بانک","school":"مدرسه","appointment":"قرار/ملاقات"}},
        "home":{"title":"🏠 خانه","subs":{"clean":"نظافت","repair":"تعمیرات","family":"خانواده"}}
    }}
}

MIND = {
 "mind":["🧠 فریب ذهن\n\nذهن می‌خواهد دائم در بازار باشد؛ اما بازار کار خودش را می‌کند. تو نباید دائم در بازار باشی.","🧠 شمع بلند\n\nذهن به‌راحتی فریب یک شمع بلند را می‌خورد. شمع بلند دلیل ورود نیست."],
 "business":["🏪 والمارت خانگی\n\nتو یک والمارت خانگی داری. والمارت هم همه موجودی‌اش را در یک ساعت نمی‌فروشد.","🏴‍☠️ گنج بازار\n\nبرای گنج وارد می‌شوم؛ نه برای جنگ. سهمم را برمی‌دارم و برمی‌گردم."],
 "setup":["📊 ستاپ\n\nجهت تایم بالا، کانال، میانگین، اصلاح، حد زیان کوچک، خروج سریع.","📐 کانال\n\nکف کانال در روند صعودی محل جستجوی خرید است؛ سقف کانال در روند نزولی محل جستجوی فروش."],
 "risk":["⚖️ حجم\n\nنه در یک نقطه، نه در یک قیمت، نه در یک لحظه، همه حجم را وارد نکن.","🛑 حد زیان\n\nحد زیان یعنی: من اشتباه بودن را می‌پذیرم و حسابم را حفظ می‌کنم."]
}

def n(): return datetime.now(TZ)
def iso(): return n().isoformat(timespec="seconds")
def dt(s): return datetime.fromisoformat(s)

def load(path, default):
    if not os.path.exists(path):
        save(path, default); return json.loads(json.dumps(default, ensure_ascii=False))
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return json.loads(json.dumps(default, ensure_ascii=False))
def save(path, data):
    with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
def cfg(): return load(CONFIG_FILE, DEFAULT_CONFIG)
def dur(sec):
    m=int(float(sec)//60); h=m//60; mm=m%60
    return f"{h} ساعت و {mm} دقیقه" if h and mm else (f"{h} ساعت" if h else f"{mm} دقیقه")
def key(t):
    s=t.strip().lower().replace(" ","_").replace("/","_").replace(":","_")
    s="".join(c for c in s if c.isalnum() or c in "_-")
    return s[:30] or "item_"+str(int(n().timestamp()))

def root_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏴‍☠️ Trading Mind Master",callback_data="root:mind")],
                                 [InlineKeyboardButton("🧠 Personal Life OS",callback_data="root:life")]])
def mind_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🧠 ذهن",callback_data="mind:mind"),InlineKeyboardButton("🏪 بیزینس",callback_data="mind:business")],
                                 [InlineKeyboardButton("📊 ستاپ",callback_data="mind:setup"),InlineKeyboardButton("🛡 ریسک",callback_data="mind:risk")],
                                 [InlineKeyboardButton("🎲 پیام تصادفی",callback_data="mind:random")],
                                 [InlineKeyboardButton("🏠 منوی اصلی",callback_data="root")]])
def life_menu():
    c=cfg(); rows=[[InlineKeyboardButton(v["title"],callback_data=f"act:{k}")] for k,v in c.items()]
    rows += [[InlineKeyboardButton("📊 گزارش امروز",callback_data="report:today"),InlineKeyboardButton("⏹ پایان فعال",callback_data="stop")],
             [InlineKeyboardButton("⏰ ریمایندر",callback_data="rem:menu"),InlineKeyboardButton("📝 یادداشت‌ها",callback_data="notes:list")],
             [InlineKeyboardButton("➕ افزودن بخش اصلی",callback_data="add:activity")],
             [InlineKeyboardButton("🏠 منوی اصلی",callback_data="root")]]
    return InlineKeyboardMarkup(rows)
def subject_menu(a):
    c=cfg(); rows=[[InlineKeyboardButton(v["title"],callback_data=f"subj:{a}:{k}")] for k,v in c[a]["subjects"].items()]
    if a=="trading": rows.append([InlineKeyboardButton("➕ افزودن نماد",callback_data="add:trading_symbol")])
    rows += [[InlineKeyboardButton("➕ افزودن موضوع",callback_data=f"add:subject:{a}")],
             [InlineKeyboardButton("📝 یادداشت برای این بخش",callback_data=f"note:activity:{a}")],
             [InlineKeyboardButton("⬅️ برگشت",callback_data="root:life")]]
    return InlineKeyboardMarkup(rows)
def sub_menu(a,s):
    c=cfg(); rows=[[InlineKeyboardButton(v,callback_data=f"item:{a}:{s}:{k}")] for k,v in c[a]["subjects"][s]["subs"].items()]
    rows += [[InlineKeyboardButton("➕ افزودن زیرموضوع",callback_data=f"add:sub:{a}:{s}")],
             [InlineKeyboardButton("📝 یادداشت برای این موضوع",callback_data=f"note:subject:{a}:{s}")],
             [InlineKeyboardButton("⬅️ برگشت",callback_data=f"act:{a}")]]
    return InlineKeyboardMarkup(rows)
def item_menu(a,s,sub):
    return InlineKeyboardMarkup([[InlineKeyboardButton("▶️ شروع",callback_data=f"startsession:{a}:{s}:{sub}")],
                                 [InlineKeyboardButton("📝 یادداشت برای این مورد",callback_data=f"note:item:{a}:{s}:{sub}")],
                                 [InlineKeyboardButton("➕ افزودن زیرموضوع جدید",callback_data=f"add:sub:{a}:{s}")],
                                 [InlineKeyboardButton("⬅️ برگشت",callback_data=f"subj:{a}:{s}")]])
def reminder_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📅 تاریخ مشخص",callback_data="rem:add:once")],
                                 [InlineKeyboardButton("🔁 روزانه",callback_data="rem:add:daily")],
                                 [InlineKeyboardButton("📆 هفتگی",callback_data="rem:add:weekly")],
                                 [InlineKeyboardButton("🗓 ماهانه",callback_data="rem:add:monthly")],
                                 [InlineKeyboardButton("📋 لیست ریمایندرها",callback_data="rem:list")],
                                 [InlineKeyboardButton("⬅️ برگشت",callback_data="root:life")]])

def set_pending(uid, action, payload):
    st=load(STATE_FILE,{})
    st[str(uid)]={"action":action,"payload":payload}
    save(STATE_FILE,st)
def pop_pending(uid):
    st=load(STATE_FILE,{})
    v=st.pop(str(uid),None); save(STATE_FILE,st); return v

def rem_help(t):
    return {"once":"مثال:\n2026-06-20 09:30 پرداخت بیمه",
            "daily":"مثال:\n21:00 ژورنال شب",
            "weekly":"مثال:\nMON 09:00 گزارش هفتگی\nروزها: MON TUE WED THU FRI SAT SUN",
            "monthly":"مثال:\n1 09:00 پرداخت اجاره"}[t]
def make_rem(t,text,chat_id):
    p=text.split()
    if t=="once":
        nd=datetime.strptime(p[0]+" "+p[1],"%Y-%m-%d %H:%M").replace(tzinfo=TZ); msg=" ".join(p[2:])
        return {"id":str(int(n().timestamp()*1000)),"chat_id":chat_id,"type":t,"message":msg,"next_time":nd.isoformat(timespec="seconds")}
    if t=="daily":
        hhmm=p[0]; h,m=map(int,hhmm.split(":")); msg=" ".join(p[1:]); nd=n().replace(hour=h,minute=m,second=0,microsecond=0)
        if nd<=n(): nd+=timedelta(days=1)
        return {"id":str(int(n().timestamp()*1000)),"chat_id":chat_id,"type":t,"message":msg,"time":hhmm,"next_time":nd.isoformat(timespec="seconds")}
    if t=="weekly":
        days={"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5,"SUN":6}; day=p[0].upper(); hhmm=p[1]; h,m=map(int,hhmm.split(":")); msg=" ".join(p[2:])
        delta=(days[day]-n().weekday())%7; nd=n().replace(hour=h,minute=m,second=0,microsecond=0)+timedelta(days=delta)
        if nd<=n(): nd+=timedelta(days=7)
        return {"id":str(int(n().timestamp()*1000)),"chat_id":chat_id,"type":t,"message":msg,"day":day,"time":hhmm,"next_time":nd.isoformat(timespec="seconds")}
    if t=="monthly":
        day=int(p[0]); hhmm=p[1]; h,m=map(int,hhmm.split(":")); msg=" ".join(p[2:]); y=n().year; mo=n().month
        while True:
            try:
                nd=n().replace(year=y,month=mo,day=day,hour=h,minute=m,second=0,microsecond=0)
                if nd>n(): break
            except ValueError: pass
            mo+=1
            if mo==13: mo=1; y+=1
        return {"id":str(int(n().timestamp()*1000)),"chat_id":chat_id,"type":t,"message":msg,"day":day,"time":hhmm,"next_time":nd.isoformat(timespec="seconds")}
def advance(r):
    cur=dt(r["next_time"])
    if r["type"]=="once": r["done"]=True
    elif r["type"]=="daily": r["next_time"]=(cur+timedelta(days=1)).isoformat(timespec="seconds")
    elif r["type"]=="weekly": r["next_time"]=(cur+timedelta(days=7)).isoformat(timespec="seconds")
    elif r["type"]=="monthly":
        mo=cur.month+1; y=cur.year
        if mo==13: mo=1; y+=1
        while True:
            try: 
                r["next_time"]=cur.replace(year=y,month=mo,day=r["day"]).isoformat(timespec="seconds"); break
            except ValueError:
                mo+=1
                if mo==13: mo=1; y+=1

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سیستم اصلی:",reply_markup=root_menu())

async def text_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    state=pop_pending(update.effective_user.id); text=update.message.text.strip()
    if not state:
        await update.message.reply_text("برای شروع /start را بزن.")
        return
    c=cfg(); act=state["action"]; payload=state["payload"]
    if act=="add_activity":
        k=key(text); c[k]={"title":text,"subjects":{"default":{"title":"عمومی","subs":{"general":"عمومی"}}}}; save(CONFIG_FILE,c)
        await update.message.reply_text(f"✅ بخش اضافه شد: {text}",reply_markup=life_menu()); return
    if act=="add_subject":
        a=payload["activity"]; k=key(text); c[a]["subjects"][k]={"title":text,"subs":{"general":"عمومی"}}; save(CONFIG_FILE,c)
        await update.message.reply_text(f"✅ موضوع اضافه شد: {text}",reply_markup=subject_menu(a)); return
    if act=="add_sub":
        a=payload["activity"]; s=payload["subject"]; k=key(text); c[a]["subjects"][s]["subs"][k]=text; save(CONFIG_FILE,c)
        await update.message.reply_text(f"✅ زیرموضوع اضافه شد: {text}",reply_markup=sub_menu(a,s)); return
    if act=="add_trading_symbol":
        k=key(text.upper()); c["trading"]["subjects"][k]={"title":text.upper(),"subs":{"analysis":"تحلیل","live":"معامله زنده","journal":"ژورنال معامله","backtest":"بک‌تست"}}; save(CONFIG_FILE,c)
        await update.message.reply_text(f"✅ نماد اضافه شد: {text.upper()}",reply_markup=subject_menu("trading")); return
    if act.startswith("note_"):
        notes=load(NOTES_FILE,[]); notes.append({"time":iso(),"type":act,"payload":payload,"text":text}); save(NOTES_FILE,notes)
        await update.message.reply_text("✅ یادداشت ثبت شد.",reply_markup=life_menu()); return
    if act=="reminder":
        try:
            reminders=load(REMINDERS_FILE,[]); reminders.append(make_rem(payload["type"],text,update.effective_chat.id)); save(REMINDERS_FILE,reminders)
            await update.message.reply_text("✅ ریمایندر ثبت شد.",reply_markup=reminder_menu())
        except Exception:
            await update.message.reply_text("فرمت درست نبود.\n\n"+rem_help(payload["type"]))
        return

async def button_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); data=q.data; c=cfg()
    if data=="root": await q.message.reply_text("سیستم اصلی:",reply_markup=root_menu()); return
    if data=="root:mind": await q.message.reply_text("🏴‍☠️ Trading Mind Master:",reply_markup=mind_menu()); return
    if data=="root:life": await q.message.reply_text("🧠 Personal Life OS:",reply_markup=life_menu()); return
    if data.startswith("mind:"):
        k=data.split(":")[1]
        msg=random.choice([x for arr in MIND.values() for x in arr]) if k=="random" else random.choice(MIND[k])
        await q.message.reply_text(msg,reply_markup=mind_menu()); return
    if data.startswith("act:"):
        a=data.split(":")[1]; await q.message.reply_text(f"{c[a]['title']}\nموضوع را انتخاب کن:",reply_markup=subject_menu(a)); return
    if data.startswith("subj:"):
        _,a,s=data.split(":"); await q.message.reply_text("زیرموضوع را انتخاب کن:",reply_markup=sub_menu(a,s)); return
    if data.startswith("item:"):
        _,a,s,sub=data.split(":"); await q.message.reply_text("انتخاب شد:",reply_markup=item_menu(a,s,sub)); return
    if data.startswith("startsession:"):
        _,a,s,sub=data.split(":"); uid=str(q.from_user.id); store=load(DATA_FILE,{"active":{},"sessions":[]})
        if uid in store["active"]:
            ac=store["active"][uid]; await q.message.reply_text(f"⚠️ یک فعالیت فعال داری:\n{ac['activity_title']} / {ac['subject_title']} / {ac['sub_title']}",reply_markup=life_menu()); return
        active={"activity":a,"subject":s,"sub":sub,"activity_title":c[a]["title"],"subject_title":c[a]["subjects"][s]["title"],"sub_title":c[a]["subjects"][s]["subs"][sub],"start_time":iso()}
        store["active"][uid]=active; save(DATA_FILE,store)
        await q.message.reply_text(f"▶️ شروع شد:\n{active['activity_title']} / {active['subject_title']} / {active['sub_title']}\n{dt(active['start_time']).strftime('%Y-%m-%d %H:%M')}",
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏹ پایان",callback_data="stop")],[InlineKeyboardButton("🏠 Life OS",callback_data="root:life")]])); return
    if data=="stop":
        uid=str(q.from_user.id); store=load(DATA_FILE,{"active":{},"sessions":[]})
        if uid not in store["active"]: await q.message.reply_text("فعالیت فعالی وجود ندارد.",reply_markup=life_menu()); return
        ac=store["active"].pop(uid); en=iso(); st=dt(ac["start_time"]); d=(dt(en)-st).total_seconds()
        sess=dict(ac); sess.update({"end_time":en,"duration_seconds":d,"date":st.strftime("%Y-%m-%d")}); store["sessions"].append(sess); save(DATA_FILE,store)
        await q.message.reply_text(f"⏹ پایان یافت:\n{ac['activity_title']} / {ac['subject_title']} / {ac['sub_title']}\nمدت: {dur(d)}",reply_markup=life_menu()); return
    if data.startswith("add:"):
        p=data.split(":"); kind=p[1]
        if kind=="activity": set_pending(q.from_user.id,"add_activity",{}); await q.message.reply_text("نام بخش اصلی جدید را بنویس:")
        elif kind=="subject": set_pending(q.from_user.id,"add_subject",{"activity":p[2]}); await q.message.reply_text("نام موضوع جدید را بنویس:")
        elif kind=="sub": set_pending(q.from_user.id,"add_sub",{"activity":p[2],"subject":p[3]}); await q.message.reply_text("نام زیرموضوع جدید را بنویس:")
        elif kind=="trading_symbol": set_pending(q.from_user.id,"add_trading_symbol",{}); await q.message.reply_text("نماد جدید را بنویس. مثال: GBPJPY")
        return
    if data.startswith("note:"):
        p=data.split(":"); set_pending(q.from_user.id,"note_"+p[1],{"parts":p[2:]}); await q.message.reply_text("یادداشتت را بنویس:"); return
    if data=="notes:list":
        notes=load(NOTES_FILE,[])[-10:]
        txt="یادداشتی ثبت نشده." if not notes else "📝 آخرین یادداشت‌ها:\n\n"+"\n".join([f"• {x['time'][:16]} - {x['text']}" for x in notes])
        await q.message.reply_text(txt,reply_markup=life_menu()); return
    if data=="report:today": await send_today(q.message); return
    if data=="rem:menu": await q.message.reply_text("⏰ ریمایندر:",reply_markup=reminder_menu()); return
    if data.startswith("rem:add:"):
        t=data.split(":")[2]; set_pending(q.from_user.id,"reminder",{"type":t}); await q.message.reply_text(rem_help(t)); return
    if data=="rem:list":
        rs=load(REMINDERS_FILE,[])
        txt="ریمایندری ثبت نشده." if not rs else "📋 ریمایندرها:\n\n"+"\n".join([f"• {r['type']} | {r['next_time'][:16]} | {r['message']}" for r in rs[-15:]])
        await q.message.reply_text(txt,reply_markup=reminder_menu()); return

async def send_today(message):
    today=n().strftime("%Y-%m-%d"); store=load(DATA_FILE,{"active":{},"sessions":[]}); ss=[s for s in store["sessions"] if s.get("date")==today]
    if not ss: await message.reply_text("برای امروز هنوز فعالیتی ثبت نشده.",reply_markup=life_menu()); return
    totals={}
    for s in ss:
        k=f"{s['activity_title']} / {s['subject_title']} / {s['sub_title']}"; totals[k]=totals.get(k,0)+float(s["duration_seconds"])
    await message.reply_text("📊 گزارش امروز - "+today+"\n\n"+"\n".join([f"• {k}: {dur(v)}" for k,v in totals.items()]),reply_markup=life_menu())

async def today_cmd(update,context): await send_today(update.message)
async def help_cmd(update,context): await update.message.reply_text("/start - منوی اصلی\n/today - گزارش امروز\n/help - راهنما")

async def reminder_checker(context):
    rs=load(REMINDERS_FILE,[]); changed=False
    for r in rs:
        if r.get("done"): continue
        if dt(r["next_time"])<=n():
            await context.bot.send_message(chat_id=r["chat_id"],text="⏰ یادآوری:\n\n"+r["message"])
            advance(r); changed=True
    if changed: save(REMINDERS_FILE,[r for r in rs if not r.get("done")])
async def post_init(app):
    await app.bot.set_my_commands([BotCommand("start","منوی اصلی"),BotCommand("today","گزارش امروز"),BotCommand("help","راهنما")])
    app.job_queue.run_repeating(reminder_checker,interval=60,first=10)

def main():
    if not TOKEN: raise ValueError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")
    app=Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("today",today_cmd)); app.add_handler(CommandHandler("help",help_cmd))
    app.add_handler(CallbackQueryHandler(button_handler)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_handler))
    print("Enhanced Combined Bot is running..."); app.run_polling()
if __name__=="__main__": main()
