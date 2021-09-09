import os
from os import path
from typing import Callable

import aiofiles
import aiohttp
import ffmpeg
import requests
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch

from vincenzo.config import ARQ_API_KEY, DURATION_LIMIT, KENKAN, SUPPORT_GROUP
from vincenzo.config import UPDATES_CHANNEL as updateschannel
from vincenzo.config import que
from vincenzo.function.admins import admins as a
from vincenzo.helpers.admins import get_administrators
from vincenzo.helpers.channelmusic import get_chat_id
from vincenzo.helpers.decorators import authorized_users_only, errors
from vincenzo.helpers.errors import DurationLimitError
from vincenzo.helpers.filters import command, other_filters
from vincenzo.helpers.gets import get_file_name, get_url
from vincenzo.services.callsmusic import callsmusic, queues
from vincenzo.services.callsmusic.callsmusic import client as USER
from vincenzo.services.converter.converter import convert
from vincenzo.services.downloaders import youtube

aiohttpsession = aiohttp.ClientSession()
chat_id = None
arq = ARQ("https://thearq.tech", ARQ_API_KEY, aiohttpsession)

useer = "Musik"


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("YOU ARE NOT ALLOWED!!!", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("./etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((30, 550), f"TITLE : {title}", (255, 215, 0), font=font)
    draw.text((30, 590), f"DURATION : {duration}", (255, 215, 0), font=font)
    draw.text((30, 630), f"VIEWERS : {views}", (255, 215, 0), font=font)
    draw.text(
        (30, 670),
        f"REQUEST : {requested_by}",
        (255, 215, 0),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(filters.command("playlist") & filters.group & ~filters.edited)
async def playlist(client, message):
    global que
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("Player is idle")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**CURRENT SONG--** di {}".format(message.chat.title)
    msg += "\n• " + now_playing
    msg += "\n• Req by " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**SONG QUEUED**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n• {name}"
            msg += f"\n• Req by {usr}\n"
    await message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("????????", callback_data="playlist"),
                    InlineKeyboardButton(
                        "?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "???????", url=f"https://t.me/{updateschannel}"
                    ),
                    InlineKeyboardButton(
                        "?????", url="https://t.me/koii_nhi_apnaa"
                    ),
                ],
            ]
       )


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=150):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "SETTINGS FROM **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "Volume : {}%\n".format(vol)
            stats += "SONGS IN QUEUE : `{}`\n".format(len(que))
            stats += "PLAYING SONGS : **{}**\n".format(queue[0][0])
            stats += "Requested by : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


@Client.on_message(filters.command("current") & filters.group & ~filters.edited)
async def ee(client, message):
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("**PLEASE TURN ON THE VC FIRST...**")


@Client.on_message(filters.command("player") & filters.group & ~filters.edited)
@authorized_users_only
async def settings(client, message):
    playing = None
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        playing = True
    queue = que.get(chat_id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("**PLEASE TURN ON THE VC FIRST!**")


@Client.on_callback_query(filters.regex(pattern=r"^(playlist)$"))
async def p_cb(b, cb):
    global que
    que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("**NOT PLAYING SONGS**")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**CURRENTLY PLAYING** di {}".format(cb.message.chat.title)
        msg += "\n• " + now_playing
        msg += "\n• Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**SONG QUEUED**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n• {name}"
                msg += f"\n• Req by {usr}\n"
        await cb.message.edit(
            msg,
            reply_markup=InlineKeyboardMarkup(
                   [
                [
                    InlineKeyboardButton("????????", callback_data="playlist"),
                    InlineKeyboardButton(
                        "?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "???????", url=f"https://t.me/{updateschannel}"
                    ),
                    InlineKeyboardButton(
                        "?????", url="https://t.me/koii_nhi_apnaa"
                    ),
                ],
            ]
       )


@Client.on_callback_query(
    filters.regex(pattern=r"^(play|pause|skip|leave|puse|resume|menu|cls)$")
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
        chet_id = cb.message.chat.id
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "pause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Music Paused!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "play":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Music Resumed!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Player is idle")
        temp = []
        for t in queue:
            temp.append(t)
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

    elif type_ == "resume":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Chat is not connected or already playng", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Music Resumed!")
    elif type_ == "puse":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Chat is not connected or already paused", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Music Paused!")
    elif type_ == "cls":
        await cb.answer("Closed menu")
        await cb.message.delete()

    elif type_ == "skip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.leave_group_call(chet_id)

                await cb.message.edit("- No More Playlist..\n- Leaving VC!")
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("Skipped")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- Skipped track\n- Now Playing **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chet_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.leave_group_call(chet_id)
            await cb.message.edit("Successfully Left the Chat!")
        else:
            await cb.answer("Chat is not connected!", show_alert=True)


@Client.on_message(command(["ytplay", "yt", "p"]) & other_filters)
@errors
async def play(_, message: Message):
    global que
    lel = await message.reply("?? **Sedang Memproses Lagu**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

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
                        "<b>ADD ASSISTANT BOT TO CHANNEL</b>",
                    )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>ADD ME AS A GROUP ADIN FIRST</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>ASSISTANT BOT SUCCESSFULLY JOINED....NOW LET'S ROCK....</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>? Flood Wait Error ?\n{user.first_name} can't join
 your group due to the large number of join requests for userbot!
                                   **OR:**
Make sure the user is not banned in the group!"
                        "\n\nADD ASSISTANT BOT MANUALLY AND TRY AGAIN...  SORRY FOR THIS INCONVINIENCE....</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} got banned from this group, ask admin to

unbann assistant bot then add Assistant Bot manually.</i>"
        )
        return
    message.from_user.id
    message.from_user.first_name
    text_links = None
    await lel.edit("?? **SEARCHING FOR SONGS**")
    message.from_user.id
    if message.reply_to_message:
        entities = []
        toxt = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == "url"]
        text_links = [entity for entity in entities if entity.type == "text_link"]
    else:
        urls = None
    if text_links:
        urls = True
    user_id = message.from_user.id
    message.from_user.first_name
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"? **VIDEOS WITH DURATION MORE THAN** `{DURATION_LIMIT}` **MINUTES CAN'T BE PPLAYED!!!!!**"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("?? ????????", callback_data="playlist"),
                    InlineKeyboardButton(
                        "?? ?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "?? ???????", url=f"https://t.me/{updateschannel}"
                    ),
                    InlineKeyboardButton(
                        "?? ????????", url="https://trakteer.id/kenkansaja/tip"
                    ),
                ],
                [InlineKeyboardButton(text="?? ?????", callback_data="cls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/744ec1f5f15768fd3cc0b.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("**PROCESSING SONG**")
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
                "**Song Not Found.....**Try searching with a clearer song title, Type `/help` if you need help!!!!!!!!!!"
            )
            print(str(e))
            return
        dlurl = url
        dlurl = dlurl.replace("youtube", "youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("????????", callback_data="playlist"),
                    InlineKeyboardButton(
                        "?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "???????", url=f"https://t.me/{updateschannel}"
                ),
                   InlineKeyboardButton(
                        "?????", url="https://t.me/koii_nhi_apnaa")
                ],
        ]
        ) 
              
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("**PROCESSING SONG**")
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
                "**Song not found.** Try searching with a clearer song title, Type `/help` if you need help"
            )
            print(str(e))
            return
        dlurl = url
        dlurl = dlurl.replace("youtube", "youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("????????", callback_data="playlist"),
                    InlineKeyboardButton(
                        "?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "???????", url=f"https://t.me/{updateschannel}"
                    ),
                    InlineKeyboardButton(
                        "?????", url="https://t.me/koii_nhi_apnaa"
                    )                
               ],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
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
            caption=f"?? **TITLE :** [{title[:60]}]({url})\n**? DURATION :** {duration}\n"
            + f"?? **QUEUED SUCESSFULLY:** {position}!\n?? **POSITION :** {requested_by}",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("Group Voice Chat is not active, I can't
join")
            return
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption=f"?? **TITLE:** [{title[:60]}]({url})\n? **DURATION:** {duration}\n?? **Status:** PLAYING\n"
            + f"?? **Requested By:** {message.from_user.mention}",
        )
        return await lel.delete()
        os.remove("final.png")


@Client.on_message(command("lplay") & other_filters)
@errors
async def stream(_, message: Message):

    lel = await message.reply("?? **processing** sound...")
    message.from_user.id
    message.from_user.first_name

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("????????", callback_data="playlist"),
                InlineKeyboardButton("?????", url=f"https://t.me/{SUPPORT_GROUP}"),
            ],
            [
                InlineKeyboardButton("???????", url=f"https://t.me/{updateschannel}"),
                InlineKeyboardButton(
                    "owner", url="https://t.me/koii_nhi_apnaa"
                ),
            ],
        ]
    )

    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"? Videos longer than {DURATION_LIMIT} minute(s) aren't allowed to play!"
            )

        file_name = get_file_name(audio)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif url:
        file_path = await convert(youtube.download(url))
    else:
        return await lel.edit_text("PLEASE GIVE ME THE SONG TO BE PLAYED!!")

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
            photo=f"{vincenzo}",
            caption=f"**THE SONG U REQUESTED WILL BE PLAYED IN POSITION:-)** `{position}`",
            reply_markup=keyboard,
        )
        return await lel.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
            photo=f"{vincenzo}",
            reply_markup=keyboard,
            caption="?? **PLAYING REQUESTED SONG.:** {}!".format(
                message.from_user.mention()
            ),
        )
        return await lel.delete()
