import os
from os import path

import requests
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, 

InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch

from vincenzo.config import ASSISTANT_NAME, DURATION_LIMIT
from vincenzo.config import SUPPORT_GROUP as groupsupport
from vincenzo.config import UPDATES_CHANNEL as updateschannel
from vincenzo.config import que
from vincenzo.helpers.admins import get_administrators
from vincenzo.helpers.decorators import authorized_users_only, 

errors
from vincenzo.helpers.errors import DurationLimitError
from vincenzo.helpers.gets import get_file_name
from vincenzo.modules.play import cb_admin_check, generate_cover
from vincenzo.services.callsmusic import callsmusic, queues
from vincenzo.services.callsmusic.callsmusic import client as USER
from vincenzo.services.converter.converter import convert
from vincenzo.services.downloaders import youtube

chat_id = None


@Client.on_message(
    filters.command(["channelplaylist", "cplaylist"]) & filters.group & 

~filters.edited
)
async def playlist(client, message):
    try:
        lel = await client.get_chat(message.chat.id)
        lol = lel.linked_chat.id
    except:
        message.reply("**IS THIS CHANNEL CONNECTED?**")
        return
    global que
    queue = que.get(lol)
    if not queue:
        await message.reply_text("Assistant BOT IS READY....")
    temp = list(queue)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**Now Playing** in {}".format(lel.linked_chat.title)
    msg += "\n- " + now_playing
    msg += "\n- Req by " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**Queue**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\n- Req by {usr}\n"
    await message.reply_text(msg)


# ============================= Settings 

=========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "Settings of **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "Volume : {}%\n".format(vol)
            stats += "Songs in queue : `{}`\n".format(len(que))
            stats += "Now Playing : **{}**\n".format(queue[0][0])
            stats += "Requested by : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇽", "cleave"),
                InlineKeyboardButton("||", "cpuse"),
                InlineKeyboardButton(">", "cresume"),
                InlineKeyboardButton(">>", "cskip"),
            ],
            [
                InlineKeyboardButton("ᴘʟᴀʏʟɪsᴛ", "cplaylist"),
            ],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", "ccls")],
        ]
    )


@Client.on_message(
    filters.command(["channelcurrent", "ccurrent"]) & filters.group & 

~filters.edited
)
async def ee(client, message):
    try:
        lel = await client.get_chat(message.chat.id)
        lol = lel.linked_chat.id
        conv = lel.linked_chat
    except:
        await message.reply("IS THIS CHAT CONNECTED?")
        return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("**ERROR OCCURED...CHECK WHETHER VC 

IS ON....**")


@Client.on_message(
    filters.command(["channelplayer", "cplayer"]) & filters.group & 

~filters.edited
)
@authorized_users_only
async def settings(client, message):
    try:
        lel = await client.get_chat(message.chat.id)
        lol = lel.linked_chat.id
        conv = lel.linked_chat
    except:
        await message.reply("IS THIS CHAT CONNECTED?")
        return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        playing = None
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("ERROR OCCURED....CHECK WHETHER VC 

IS TURNED ON...")


@Client.on_callback_query(filters.regex(pattern=r"^(cplaylist)$"))
async def p_cb(b, cb):
    global que
    try:
        lel = await client.get_chat(cb.message.chat.id)
        lol = lel.linked_chat.id
        conv = lel.linked_chat
    except:
        return
    que.get(lol)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(lol)
        if not queue:
            await cb.message.edit("ASSISTANT IS READY....LETS GO...")
        temp = list(queue)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Now Playing** in {}".format(conv.title)
        msg += "\n- " + now_playing
        msg += "\n- Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Queue**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Req by {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(cplay|cpause|cskip|cleave|cpuse|

cresume|cmenu|ccls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
        try:
            lel = await b.get_chat(cb.message.chat.id)
            lol = lel.linked_chat.id
            conv = lel.linked_chat
            chet_id = lol
        except:
            return
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1]

[0].callback_data
    if type_ == "cpause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("CHAT NOT CONNECTED DUDE!", 

show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Music Paused!")
            await cb.message.edit(updated_stats(conv, qeue), 

reply_markup=r_ply("play"))

    elif type_ == "cplay":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("CHAT IS NOT CONNECTED DUDE!", 

show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Music Resumed!")
            await cb.message.edit(
                updated_stats(conv, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "cplaylist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Player is idle")
        temp = list(queue)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Now Playing** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\n- Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Queue**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Req by {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "cresume":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer(
                "ERROR- EITHER CHAT IS NOT CONNECTED OR ALREADY 

PLAYING...", show_alert=True
            )
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Music Resumed!")
    elif type_ == "cpuse":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer(
                "CHAT IS NOT CONNECTED OR VC IS PAUSED...TYPE /resume 

TO CONTINUE...", show_alert=True
            )
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Music Paused!")
    elif type_ == "ccls":
        await cb.answer("Closed menu")
        await cb.message.delete()

    elif type_ == "cmenu":
        stats = updated_stats(conv, qeue)
        await cb.answer("Menu opened")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(">_<", "cleave"),
                    InlineKeyboardButton("!!", "cpuse"),
                    InlineKeyboardButton("▶️", "cresume"),
                    InlineKeyboardButton("▶▶", "cskip"),
                ],
                [
                    InlineKeyboardButton("Playlist !!", "cplaylist"),
                ],
                [InlineKeyboardButton("Close", "ccls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "cskip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("CHAT IS NOT CONNECTED...", 

show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.leave_group_call(chet_id)

                await cb.message.edit(
                    "NO MORE PLAYLIST..\n- LEAVING VC....!"
                )
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("Skipped")
                await cb.message.edit((m_chat, qeue), 

reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- Skipped track\n- Now Playing **{qeue[0][0]}**"
                )

    elif chet_id in callsmusic.pytgcalls.active_calls:
        try:
            callsmusic.queues.clear(chet_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chet_id)
        await cb.message.edit("SUCCESSFULLY LEFT THE CHAT!!")
    else:
        await cb.answer("CHAT NOT CONNECTED!", show_alert=True)


@Client.on_message(
    filters.command(["channelplay", "cplay"]) & filters.group & 

~filters.edited
)
@authorized_users_only
@errors
async def play(_, message: Message):
    global que
    lel = await message.reply(">_< **Processing**")

    try:
        conchat = await _.get_chat(message.chat.id)
        conv = conchat.linked_chat
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply(">_< IS THIS CHAT CONNECTED? ")
        return
    try:
        administrators = await get_administrators(conv)
    except:
        await message.reply(":( AM I ADMIN IN THIS CHANNEL?..")
    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>!!!REMEMBER TO ADD @{ASSISTANT_NAME} TO 

THIS CHAT!!!</b>",
                    )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b> >_< MAKE ME ADMIN IN THIS CHANNEL 

FIRST....</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b> :) ASSISTANT JOINED THE CHAT SUCCESSFULLY...</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b> !!Flood Wait Error!! \nSORRY.. 

{user.first_name} BOT CAN'T JOIN THE CHANNEL **DUE TO LARGE NUMBER OF REQUESTS FOR THE MUSIC BOT!!     
                             ELSE:
MAKE SURE THAT BOT IS NOT BLOCKED IN THE CHANNEL......**"
                        "\n\nIF PROBLEM STILL OCCURS ADD ASSISTANT BOT MANUALLY....>_<...</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} Userbot is not in this chat,
Ask the Channel admin to send the command /play for the first time
time or add {user.first_name} manually</i>"
        )
        return
    message.from_user.id
    text_links = None
    message.from_user.first_name
    await lel.edit("**Finding!!**")
    message.from_user.id
    user_id = message.from_user.id
    message.from_user.first_name
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if message.reply_to_message:
        entities = []
        toxt = message.reply_to_message.text or 

message.reply_to_message.caption
        if (
            message.reply_to_message.entities
            or message.reply_to_message.caption_entities
        ):
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == "url"]
        text_links = [entity for entity in entities if entity.type == 

"text_link"]
    else:
        urls = None
    if text_links:
        urls = True
    audio = (
        (message.reply_to_message.audio or 

message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"VIDEOS LONGER THAN {DURATION_LIMIT} 

MINUTES CANT BE PLAYED IN VOICE CHATS!"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(":)Playlist", 

callback_data="cplaylist"),
                    InlineKeyboardButton("Menu ", 

callback_data="cmenu"),
                ],
                [InlineKeyboardButton(text="Close", 

callback_data="ccls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = 

"https://telegra.ph/file/744ec1f5f15768fd3cc0b.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, 

thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("**Processing**")
        ydl_opts = {"format": "141/bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "**SONG NOT FOUND:(** TYPE APPROPRIATE SONG NAME... ELSE TYPE `/help` IF U NEED ANY HELP...."
            )
            print(str(e))
            return
        dlurl = url
        dlurl = dlurl.replace("youtube", "youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ᴘʟᴀʏʟɪꜱᴛ", 

callback_data="playlist"),
                    InlineKeyboardButton("ɢʀᴏᴜᴘ", url=f"https://t.me/

{groupsupport}"),
                ],
                [
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{updateschannel}"
                    )
                ],
                [InlineKeyboardButton(text=">_<", 

callback_data="cls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, 

thumbnail)
        file_path = await convert(youtube.download(url))
    else:
        query = "".join(" " + str(i) for i in message.command[1:])
        print(query)
        await lel.edit(" **Processing**")
        ydl_opts = {"format": "141/bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "SONG NOT FOUND...TRY TO ENTER APROPRIATE SONG NAME AND TRY AGAIN....."
            )
            print(str(e))
            return

        dlurl = url
        dlurl = dlurl.replace("youtube", "youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ᴘʟᴀʏʟɪꜱᴛ", 

callback_data="playlist"),
                    InlineKeyboardButton("ɢʀᴏᴜᴘ", url=f"https://t.me/

{groupsupport}"),
                ],
                [
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{updateschannel}"
                    )
                ],
                [InlineKeyboardButton(text=">_<", 

callback_data="cls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, 

thumbnail)
        file_path = await convert(youtube.download(url))
    chat_id = chid
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f" **TITLE** [{title[:60]}]({url})\n? **DURATION:** 

{duration}\n?? **STATUS:** Antrian Ke `{position}`\n"
            + f"?? **REQUESTED BY:** {message.from_user.mention}",
            reply_markup=keyboard,
        )
    else:
        chat_id = chid
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption=f" **TITLE:** [{title[:60]}]({url})\n**? DURATION:** 

{duration}\n"
            + f"?? **STATUS::** Playing\n **REQUESTED BY:** 

{requested_by}".format(
                message.from_user.mention()
            ),
        )

        os.remove("final.png")
        return await lel.delete()
