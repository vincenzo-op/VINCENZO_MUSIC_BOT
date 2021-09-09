import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from vincenzo.config import SUDO_USERS
from vincenzo.helpers.filters import command
from vincenzo.services.callsmusic.callsmusic import client as USER


@Client.on_message(command("gs") & filters.user(SUDO_USERS) & ~filters.edited)
async def gcast(_, message: Message):
    sent = 0
    failed = 0
    if message.from_user.id not in SUDO_USERS:
        return
    wtf = await message.reply("SENDING A GLOBAL MESSAGE...")
    if not message.reply_to_message:
        await wtf.edit("REPLY TO ONLY TEXT MESSAGE TO GCAST....")
        return
    lmao = message.reply_to_message.text
    async for dialog in USER.iter_dialogs():
        try:
            await USER.send_message(dialog.chat.id, lmao)
            sent = sent + 1
            await wtf.edit(
                f"**SENDING A GLOBAL MESSAGE** \n\n**SENT TO:** `{sent}` chat \n**FAILED TO SEND TO:** {failed} chat"
            )
            await asyncio.sleep(0.7)
        except:
            failed = failed + 1
            await wtf.edit(
                f"`SENDING A GLOBAL MESSAGE` \n\n**SENT TO:** `{sent}` Chats \n**FAILED TO SEND TO :** {failed} Chats"
            )
            await asyncio.sleep(0.7)

    return await wtf.edit(
        f"`GCAST SUCCESSFULLY EXECUTED...` \n\n**SENT TO:** `{sent}` Chats \n**FAILED TO SEND TO:** {failed} Chats"
    )
