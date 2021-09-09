from asyncio.queues import QueueEmpty

from pyrogram import Client, filters
from pyrogram.types import Message

from vincenzo.config import BOT_USERNAME
from vincenzo.function.admins import set
from vincenzo.helpers.channelmusic import get_chat_id
from vincenzo.helpers.decorators import authorized_users_only
from vincenzo.helpers.filters import command, other_filters
from vincenzo.services.callsmusic import callsmusic


@Client.on_message(filters.command(["adminreset", f"adminreset@{BOT_USERNAME}"]))
@authorized_users_only
async def update_admin(client, message: Message):
    chat_id = get_chat_id(message.chat)
    set(
        chat_id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("!!!Admin cache refreshed!!!")


@Client.on_message(command(["pause", f"pause@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text(" **NO SONG IS PLAYING CURRRENTLY!**")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("▶️ **Paused!**")


@Client.on_message(command(["resume", f"resume@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text(" **NO SONGS ARE CURRENTLY PAUSED!!!**")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text(" **Resumed!**")


@Client.on_message(command(["end", f"end@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text(" **NO SONG IS PLAYING!!!**")
    else:
        try:
            callsmusic.queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("**STOPPED THE SONG!**")


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("**THERE IS NO ADDITIONAL SONGS TO SKIP!**")
    else:
        callsmusic.queues.task_done(chat_id)

        if callsmusic.queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, callsmusic.queues.get(chat_id)["file"]
            )

        await message.reply_text("**SKIP THE CURRENT SONG!**")


@Client.on_message(filters.command(["admincache", f"admincache@{BOT_USERNAME}"]))
@authorized_users_only
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text(" **REGISTERED ADMIN** ALREADY **UPDATED**")
