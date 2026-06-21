import time
import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from langdetect import detect

TOKEN = "8558727096:AAFJDcyWvSQRAQ7gxcVZdGW5En6PKpKHe7M"

STATE_FILE = "afk_state.json"

afk = False
afk_start_time = 0
last_reply_time = {}

def load_state():
    global afk, afk_start_time
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            afk = data.get("afk", False)
            afk_start_time = data.get("afk_start_time", 0)

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({"afk": afk, "afk_start_time": afk_start_time}, f)

async def afk_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global afk, afk_start_time
    afk = True
    afk_start_time = time.time()
    save_state()
    await update.message.reply_text("AFK включён")

async def afk_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global afk
    afk = False
    save_state()
    await update.message.reply_text("AFK выключён")

def format_time(seconds):
    m = int(seconds // 60)
    h = m // 60
    m = m % 60
    return f"{h}ч {m}м"

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global afk, last_reply_time

    if not afk:
        return

    user_id = update.message.from_user.id
    now = time.time()

    if user_id in last_reply_time:
        if now - last_reply_time[user_id] < 60:
            return

    last_reply_time[user_id] = now

    text = update.message.text

    try:
        lang = detect(text)
    except:
        lang = "unknown"

    uptime = format_time(now - afk_start_time)

    if lang == "en":
        await update.message.reply_text(f"If I ignore you, it means I'm sleeping.\nAFK: {uptime}")
    elif lang == "ru":
        await update.message.reply_text(f"Если я тебя игнорю, значит я сплю\nAFK: {uptime}")
    else:
        await update.message.reply_text(f"Услышал родной, но ща я сплю\nAFK: {uptime}")

load_state()

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("afk", afk_on))
app.add_handler(CommandHandler("back", afk_off))
app.add_handler(MessageHandler(filters.TEXT, reply))

app.run_polling()