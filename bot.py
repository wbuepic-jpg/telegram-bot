import asyncio
import logging
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message

# ലോഗിംഗ് സെറ്റപ്പ്
logging.basicConfig(level=logging.INFO)

# ബോട്ട് സെറ്റപ്പ് (നിങ്ങൾ തന്ന ടോക്കൺ ഇവിടെ ചേർത്തിട്ടുണ്ട്)
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = "8856980115:AAEJFB6A1ioyt6cnxCekTamTBR-WATwLltw"

app = Client("link_only_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# നിങ്ങൾ നൽകിയ റിയാക്ഷൻ ഇമോജികൾ
REACTIONS = ["💋", "🍓", "❤️"]


# 1. ഗ്രൂപ്പ് മെസ്സേജ് മോഡറേഷൻ (ലിങ്ക് മാത്രം അനുവദിക്കുക)
@app.on_message(filters.group & ~filters.service)
async def moderate_group(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return

    text = message.text or message.caption or ""

    # മെസ്സേജിൽ ലിങ്ക് ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
    has_link = bool(
        message.entities
        and any(
            entity.type in ["url", "text_link"] for entity in message.entities
        )
    ) or (
        "http://" in text
        or "https://" in text
        or "www." in text
        or "t.me/" in text
    )

    if has_link:
        # ലിങ്ക് ആണെങ്കിൽ ഇമോജികൾ വച്ച് റിയാക്ട് ചെയ്യുക
        for emoji in REACTIONS:
            try:
                await message.react(emoji=emoji)
                await asyncio.sleep(0.3)
            except Exception as e:
                logging.error(f"Reaction error: {e}")
    else:
        # ലിങ്ക് അല്ലെങ്കില്‍ മെസ്സേജ് ഡിലീറ്റ് ചെയ്യുക
        try:
            await message.delete()

            # 30 സെക്കൻഡ് മാത്രം നിൽക്കുന്ന വാണിംഗ് മെസ്സേജ്
            warning_msg = await message.reply(
                f"ഹലോ {user.mention}, ഈ ഗ്രൂപ്പിൽ **ലിങ്ക് മാത്രമേ** ഇടാൻ പാടുള്ളൂ!"
            )

            await asyncio.sleep(30)
            await warning_msg.delete()
        except Exception as e:
            logging.error(f"Delete/Warning error: {e}")


# 2. 24 മണിക്കൂറും ബോട്ട് ലൈവ് ആയിരിക്കാൻ വെബ് സർവറും ഓട്ടോ-പിംഗും
async def handle(request):
    return web.Response(text="Bot is running 24/7!")


async def web_server():
    web_app = web.Application()
    web_app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()


async def auto_ping():
    while True:
        await asyncio.sleep(300)
        logging.info("Bot auto-pinged to keep alive.")


async def main():
    await app.start()
    logging.info("Telegram Bot Started Successfully!")
    asyncio.create_task(web_server())
    asyncio.create_task(auto_ping())
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
