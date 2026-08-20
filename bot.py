import asyncio
import logging
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = "8856980115:AAEJFB6A1ioyt6cnxCekTamTBR-WATwLltw"

app = Client("link_only_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

REACTIONS = ["💋", "🍓", "❤️"]


@app.on_message(filters.group & ~filters.service)
async def moderate_group(client: Client, message: Message):
    user = message.from_user
    if not user:
        return

    text = message.text or message.caption or ""
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
        for emoji in REACTIONS:
            try:
                await message.react(emoji=emoji)
                await asyncio.sleep(0.3)
            except Exception as e:
                logging.error(f"Reaction error: {e}")
    else:
        try:
            await message.delete()
            warning_msg = await message.reply(
                f"ഹലോ {user.mention}, ഈ ഗ്രൂപ്പിൽ **ലിങ്ക് മാത്രമേ** ഇടാൻ പാടുള്ളൂ!"
            )
            await asyncio.sleep(30)
            await warning_msg.delete()
        except Exception as e:
            logging.error(f"Delete/Warning error: {e}")


async def handle(request):
    return web.Response(text="Bot is running 24/7!")


async def main():
    web_app = web.Application()
    web_app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    await app.start()
    logging.info("Telegram Bot Started Successfully!")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
