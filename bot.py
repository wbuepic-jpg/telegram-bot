import asyncio
import logging
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
import os

logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID", "2040"))
API_HASH = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")
BOT_TOKEN = os.getenv(
    "BOT_TOKEN", "8856980115:AAEJFB6A1ioyt6cnxCekTamTBR-WATwLltw"
)

app = Client("link_only_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

REACTIONS = ["💋", "🍓", "❤️"]

# യൂസേഴ്സ് ലിങ്ക് അയച്ച കണക്ക് സൂക്ഷിക്കാൻ
user_link_counts = {}

# ഗ്രൂപ്പിലെ അവസാനത്തെ വാണിംഗ് മെസ്സേജിന്റെ ഐഡി സേവ് ചെയ്യാൻ (പഴയത് ഡിലീറ്റ് ചെയ്യാൻ)
last_warning_msg_id = None


@app.on_message(filters.group & ~filters.service)
async def moderate_group(client: Client, message: Message):
    global last_warning_msg_id
    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return

    user_id = user.id
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
        # ലിങ്ക് ആണെങ്കിൽ റിയാക്ട് ചെയ്യുക
        for emoji in REACTIONS:
            try:
                await message.react(emoji=emoji)
                await asyncio.sleep(0.3)
            except Exception as e:
                logging.error(f"Reaction error: {e}")

        # ലിങ്ക് കൗണ്ട് കൂട്ടുക
        if user_id not in user_link_counts:
            user_link_counts[user_id] = 0
        user_link_counts[user_id] += 1

        # 4-ആമത്തെ തവണ ലിങ്ക് ഇടുമ്പോൾ മ്യൂട്ട് ചെയ്യുക
        if user_link_counts[user_id] >= 4:
            user_link_counts[user_id] = 0
            try:
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions(can_send_messages=False),
                    until_date=int(asyncio.get_event_loop().time() + 30),
                )

                # പുതിയ വാണിംഗ് അയക്കുന്നതിന് മുൻപ് പഴയ വാണിംഗ് ഉണ്ടെങ്കിൽ ഡിലീറ്റ് ചെയ്യുക
                if last_warning_msg_id:
                    try:
                        await client.delete_messages(chat_id, last_warning_msg_id)
                    except Exception:
                        pass

                warn_msg = await message.reply(
                    f"Hello da ponnahh {user.mention}, നീ ഈ ഗ്രൂപ്പിൽ മൂന്നിൽ കൂടുതൽ വട്ടം ലിങ്ക് ഇട്ടു. അതുകൊണ്ട് നീ 30 സെക്കൻഡ് മ്യൂട്ട് ആയിരിക്കൂ."
                )
                last_warning_msg_id = warn_msg.id

                await asyncio.sleep(30)

                await client.restrict_chat_member(
                    chat_id, user_id, ChatPermissions(can_send_messages=True)
                )

                unmute_msg = await message.reply(
                    f"Hello da ponnahh {user.mention}, ഇനി നീ ലിങ്ക് ഷെയർ ആക്കിക്കോ!"
                )
                await asyncio.sleep(10)
                await unmute_msg.delete()
                await warn_msg.delete()

            except Exception as e:
                logging.error(f"Mute/Unmute error: {e}")
    else:
        # ലിങ്ക് അല്ലാത്ത മെസ്സേജുകൾ ഡിലീറ്റ് ചെയ്യുക
        try:
            await message.delete()

            # പുതിയ വാണിംഗ് അയക്കുന്നതിന് മുൻപ് പഴയ വാണിംഗ് ഉണ്ടെങ്കിൽ ഉടൻ ഡിലീറ്റ് ചെയ്യുക
            if last_warning_msg_id:
                try:
                    await client.delete_messages(chat_id, last_warning_msg_id)
                except Exception:
                    pass

            # പുതിയ വാണിംഗ് മെസ്സേജ് അയക്കുന്നു
            warning_msg = await message.reply(
                f"Hello da ponnahh {user.mention} ഈ ഗ്രൂപ്പിൽ ലിങ്കുകൾ മാത്രം ഇടുക. എല്ലാവരുടെയും സഹകരണവും പിന്തുണയും പ്രതീക്ഷിക്കുന്നു, ഹാപ്പി ആയിരിക്കൂ!❤️💋"
            )
            last_warning_msg_id = warning_msg.id

            # 30 സെക്കൻഡിനു ശേഷം വാണിംഗ് മെസ്സേജ് ഓട്ടോമാറ്റിക്കായി ഡിലീറ്റ് ചെയ്യുക
            await asyncio.sleep(30)
            await warning_msg.delete()
            if last_warning_msg_id == warning_msg.id:
                last_warning_msg_id = None

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
    logging.info("Telegram Bot Started with Smart Warning Cleanup!")
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
