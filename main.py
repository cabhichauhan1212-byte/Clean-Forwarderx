# EliteX Hybrid Commander (Final with Menu)
# Features: BotFather Style Menu, 24/7 Ready

import asyncio
import logging
import os
import re
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from pyrogram.errors import FloodWait

# ────────────────────────────────────────────────
# ⚙️ CONFIGURATION ZONE
# ────────────────────────────────────────────────
API_ID = 33489674
API_HASH = "0950dc93523305a7d0044d45a4c501f2"
STRING_SESSION = "BQH_AwoASWsXQ8JhCydu_yq_yul9mfin23I53-jeC0oRAK-S8hr9NeGFRxoIp-YODkTy28CRcX2sPy-LT3l1exq4XRe0ZE9WrS4TWSgQVU9DwpqAhcFu36Lj2tpMm8Gu4_Zy2TrYlc2JvdN53Qw3K-czbzvcee1CGzFELALcCgdclZijoK8miwwi3wVK9a53CssRWPjuifbcQQ7QZIum-D0RF5ztESPtYVzhEIOJG2sBaTdiRZy7IjmnxrdnbsK7-GTzV6jl7mQNRAFLh41F6LWL16XPA-m9fM4PcvsN85z-QN9hXw95wpm4ZuoSD-ckw5HnONTDMNQ50l4AWTKcvf6L95vIIgAAAAF-aFGyAA"

# ✅ AAPKA BOT TOKEN
BOT_TOKEN = "8320848331:AAFXOL7yK_8gMsjaK3BQJk1KNMuHkAAcOj4"

VIP_FOOTER = """
━━━━━━━━━━━━━━━━━━━━
🚀 Available In VIP
⚠️ Premium / Exclusive Course

📥 For VIP & Other Paid Courses
🤖 Contact Bot : @EliteXAbhi_bot
💬 Admin : @OfficialAbhiX ✅
━━━━━━━━━━━━━━━━━━━━
"""
WHITELIST = ["elitex", "abhi"]

# ────────────────────────────────────────────────
# SETUP
# ────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EliteX")

try:
    import nest_asyncio
except ImportError:
    os.system("pip install pyrogram tgcrypto nest_asyncio")
    import nest_asyncio

nest_asyncio.apply()

# Initialize Clients
worker = Client("EliteX_Worker", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, in_memory=True)
bot = Client("EliteX_Controller", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

job_config = {
    "source": 0, "target": 0, "start_msg": 0,
    "mode": "1", "running": False, "stop": False
}

# ────────────────────────────────────────────────
# 🧠 LOGIC ENGINE
# ────────────────────────────────────────────────
def clean_text(text, mode):
    if not text: return ""
    def swap(m): return m.group() if any(w in m.group().lower() for w in WHITELIST) else "@EliteXAbhi_Bot"
    text = re.sub(r"@\w+", swap, text)
    text = re.sub(r'https?://\S+', '', text)
    if mode == "1":
        limit = 1024 
        footer_len = len(VIP_FOOTER) + 5
        if len(text) > (limit - footer_len): text = text[:(limit - footer_len)] + "..."
        return f"{text}\n\n{VIP_FOOTER.strip()}"
    return text.strip()

async def run_forwarder(chat_id, status_msg):
    job_config["running"] = True
    job_config["stop"] = False
    
    s_id = job_config["source"]
    t_id = job_config["target"]
    start_id = job_config["start_msg"]
    mode = job_config["mode"]

    try:
        last_msg = await worker.get_chat_history(s_id, limit=1).__anext__()
        end_id = last_msg.id
    except:
        await bot.edit_message_text(chat_id, status_msg.id, "❌ **Error:** Source Channel Access Failed!")
        job_config["running"] = False
        return

    await bot.edit_message_text(chat_id, status_msg.id, f"🚀 **STARTED!**\n\nFrom: `{s_id}`\nTo: `{t_id}`\nRange: {start_id} ➔ {end_id}")
    
    current_id = start_id
    success_count = 0

    while current_id <= end_id:
        if job_config["stop"]:
            await bot.send_message(chat_id, "🛑 **Job Stopped by User.**")
            break
            
        batch_end = min(current_id + 50, end_id + 1)
        ids = list(range(current_id, batch_end))
        
        try:
            msgs = await worker.get_messages(s_id, ids)
            if not isinstance(msgs, list): msgs = [msgs]

            for msg in msgs:
                if not msg or msg.empty or msg.service: continue
                
                caption = clean_text(msg.caption or msg.text or "", mode)
                
                try:
                    if mode == "3": # Clone
                        await msg.copy(t_id)
                    elif msg.text:
                        await worker.send_message(t_id, caption, disable_web_page_preview=True)
                    elif msg.photo:
                        await worker.send_photo(t_id, msg.photo.file_id, caption=caption)
                    elif msg.video:
                        await worker.send_video(t_id, msg.video.file_id, caption=caption)
                    elif msg.document:
                        await worker.send_document(t_id, msg.document.file_id, caption=caption)
                    else:
                        await msg.copy(t_id)
                    
                    success_count += 1
                    await asyncio.sleep(1.2)
                    
                except FloodWait as e:
                    await bot.send_message(chat_id, f"⏳ FloodWait: Sleeping {e.value}s")
                    await asyncio.sleep(e.value + 5)
                except Exception: pass
            
            await bot.edit_message_text(chat_id, status_msg.id, 
                f"🔄 **RUNNING...**\n\n✅ Sent: {success_count}\n📍 Current: {batch_end}/{end_id}")
            
            current_id = batch_end
            
        except Exception as e:
            print(f"Batch Error: {e}")
            current_id += 50

    job_config["running"] = False
    await bot.send_message(chat_id, "✅ **TASK COMPLETED!**")

# ────────────────────────────────────────────────
# 🎮 BOT COMMANDS
# ────────────────────────────────────────────────

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    txt = (
        f"👋 **EliteX Dashboard**\n"
        f"Status: {'🟢 Running' if job_config['running'] else '🔴 Idle'}\n\n"
        f"📥 Source: `{job_config['source']}`\n"
        f"📤 Target: `{job_config['target']}`\n"
        f"🏁 Start ID: `{job_config['start_msg']}`\n"
        f"⚙️ Mode: `{job_config['mode']}`"
    )
    btns = [
        [InlineKeyboardButton("📥 Set Source", callback_data="set_src"),
         InlineKeyboardButton("📤 Set Target", callback_data="set_tgt")],
        [InlineKeyboardButton("🏁 Set Start ID", callback_data="set_start"),
         InlineKeyboardButton("⚙️ Set Mode", callback_data="set_mode")],
        [InlineKeyboardButton("🚀 START JOB", callback_data="run"),
         InlineKeyboardButton("🛑 STOP", callback_data="stop")]
    ]
    await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(btns))

@bot.on_message(filters.command("help"))
async def help_handler(client, message):
    await message.reply_text(
        "📚 **EliteX Help Menu**\n\n"
        "Use these commands to control the bot:\n\n"
        "🔹 /start - Open the Main Dashboard\n"
        "🔹 /status - Check live progress\n"
        "🔹 /set_source - Quickly set Source Channel\n"
        "🔹 /set_target - Quickly set Target Channel\n"
        "🔹 /stop - Emergency Stop\n"
    )

@bot.on_callback_query()
async def cb_handler(client, query):
    data = query.data
    chat_id = query.message.chat.id
    
    if data == "set_src":
        await query.message.reply_text("👇 **Send Source Channel ID:**")
        job_config["awaiting"] = "source"
    elif data == "set_tgt":
        await query.message.reply_text("👇 **Send Target Channel ID:**")
        job_config["awaiting"] = "target"
    elif data == "set_start":
        await query.message.reply_text("👇 **Send Start Message ID (Number):**")
        job_config["awaiting"] = "start_msg"
    elif data == "set_mode":
        btns = [
            [InlineKeyboardButton("VIP Footer", callback_data="mode_1")],
            [InlineKeyboardButton("Clean Only", callback_data="mode_2")],
            [InlineKeyboardButton("Clone", callback_data="mode_3")]
        ]
        await query.message.edit_text("⚙️ **Select Mode:**", reply_markup=InlineKeyboardMarkup(btns))
    elif data.startswith("mode_"):
        job_config["mode"] = data.split("_")[1]
        await query.message.edit_text(f"✅ Mode Set to: {job_config['mode']}")
    elif data == "run":
        if job_config["source"] == 0 or job_config["target"] == 0:
            await query.answer("❌ Config Missing!", show_alert=True)
            return
        msg = await query.message.reply_text("⏳ **Initializing...**")
        asyncio.create_task(run_forwarder(chat_id, msg))
    elif data == "stop":
        job_config["stop"] = True
        await query.answer("🛑 Stopping...", show_alert=True)

@bot.on_message(filters.text & ~filters.command(["start", "help"]))
async def input_handler(client, message):
    if "awaiting" in job_config:
        try:
            val = int(message.text)
            key = job_config["awaiting"]
            job_config[key] = val
            del job_config["awaiting"]
            await message.reply_text(f"✅ **{key.upper()} Updated:** `{val}`\nPress /start to refresh.")
        except:
            await message.reply_text("❌ Invalid ID! Please send a number.")

# ────────────────────────────────────────────────
# 🚀 LAUNCH & MENU SETUP
# ────────────────────────────────────────────────
async def main():
    print("✅ System Online! Setting up Menu...")
    await worker.start()
    await bot.start()
    
    # 🔥 YE HAI WOH MAGIC CODE JO MENU BANAYEGA
    commands = [
        BotCommand("start", "Open Control Dashboard 🎛️"),
        BotCommand("help", "How to use this bot 📚"),
        BotCommand("status", "Check Job Status 📊"),
        BotCommand("stop", "Emergency Stop 🛑")
    ]
    await bot.set_bot_commands(commands)
    print("✅ Menu Button Added to Bot!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
  
