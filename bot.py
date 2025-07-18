import aiohttp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === CONFIG ===
TOKEN = '7708512334:AAHltdbTA632hHy2E1gQ5F4H4o-MDVGboH4'
START_NID = 4367681722
END_NID = 4969998525  # use a smaller range for testing
API_URL = "https://learn.aakashitutor.com/api/getquizfromid?nid="
BATCH_SIZE = 400 # control how many NIDs are processed in parallel

# === FUNCTION: Fetch test metadata ===
async def fetch_test_data(session, nid):
    try:
        async with session.get(f"{API_URL}{nid}", timeout=15) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, list) and data:
                    return nid, data[0].get("title", "No Title")
    except Exception:
        pass
    return nid, None

# === COMMAND: /scan ===
async def scan_nids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Starting scan...")

    async with aiohttp.ClientSession() as session:
        for i in range(START_NID, END_NID + 1, BATCH_SIZE):
            batch = range(i, min(i + BATCH_SIZE, END_NID + 1))
            tasks = [fetch_test_data(session, nid) for nid in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    continue
                nid, title = result
                if title:
                    await update.message.reply_text(f"✅ Found: {title} (NID: {nid})")
                print(f"{'FOUND' if title else 'NOT FOUND'}: NID {nid}")

    await update.message.reply_text("✅ Scan complete.")
    print("✅ Finished scanning.")

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send /scan to start scanning NIDs.")

# === MAIN ===
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan_nids))
    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
