import logging

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from vincenzo.config import (
    BOT_USERNAME,
    vincenzo,
    OWNER,
    PROJECT_NAME,
    SOURCE_CODE,
    SUPPORT_GROUP,
    UPDATES_CHANNEL,
)
from vincenzo.helpers.decorators import authorized_users_only
from vincenzo.modules.msg import Messages as tr

logging.basicConfig(level=logging.INFO)


@Client.on_message(filters.command("start") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_sticker(
        "CAACAgUAAxkBAAFF-KFg-jaEvlhu_kNknYQjxsuyDvp--AACjAMAAtpWSVeocCICILIfRSAE"
    )
    await message.reply_text(
        f"""**HELLO MY NAME IS** [{PROJECT_NAME}](https://telegra.ph/file/.jpg)
DEVELOPED BY {OWNER}
·??????????????? ·
?? I HAVE MANY FEATURES FOR THOSE WHO LIKE SONGS..
? **PLAYING SONGS IN GROUP**
? **PLAYING SONGS IN CHANNEL**
? **DOWNLOAD SONGS**
? **PLAYING SONGS FROM YOUTUBE**
・✦▭▭▭▭✧◦✦◦✧▭▭▭▭✦ ・
!!!CLICK THE HELP BUTTON FOR MORE INFORMATION!!
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("ʜᴇʟᴘ", callback_data=f"help+1"),
                    InlineKeyboardButton(
                        "ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ +"
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "ɢʀᴏᴜᴘ", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
                [
                    InlineKeyboardButton("! ɢɪᴛ ʜᴜʙ !", url=f"{SOURCE_CODE}"),
                    InlineKeyboardButton(
                        "ᴄᴏɴᴛᴀᴄᴛ", url="https://t.me/koii_nhi_apnaa"
                    ),
                ],
            ]
        ),
        reply_to_message_id=message.message_id,
    )


@Client.on_message(filters.command("start") & ~filters.private & ~filters.channel)
async def gstart(_, message: Message):
    await message.reply_photo(
        photo=f"{vincenzo}",
        caption=f"""** {PROJECT_NAME} is online**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="ᴏᴡɴᴇʀ", url=f"t.me/{OWNER}")],
                [
                    InlineKeyboardButton(
                        text="ɢʀᴏᴜᴘ", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                    InlineKeyboardButton(
                        text="ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
                [
                    InlineKeyboardButton("ɢɪᴛ ʜᴜʙ", url=f"{SOURCE_CODE}"),
                    InlineKeyboardButton(
                        "Jᴏɪɴ..", url="https://t.me/our_SECRET_SOCIETY"
                    ),
                ],
            ]
        ),
    )


@Client.on_message(filters.private & filters.incoming & filters.command(["help"]))
def _help(client, message):
    client.send_message(
        chat_id=message.chat.id,
        text=tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_web_page_preview=True,
        disable_notification=True,
        reply_markup=InlineKeyboardMarkup(map(1)),
        reply_to_message_id=message.message_id,
    )


help_callback_filter = filters.create(
    lambda _, __, query: query.data.startswith("help+")
)


@Client.on_callback_query(help_callback_filter)
def help_answer(client, callback_query):
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    msg = int(callback_query.data.split("+")[1])
    client.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=tr.HELP_MSG[msg],
        reply_markup=InlineKeyboardMarkup(map(msg)),
    )


def map(pos):
    if pos == 1:
        button = [
            [
                InlineKeyboardButton(text="????????", callback_data="help+5"),
                InlineKeyboardButton(text="????????", callback_data="help+2"),
            ]
        ]
    elif pos == len(tr.HELP_MSG) - 1:
        url = f"https://t.me/{SUPPORT_GROUP}"
        button = [
            [
                InlineKeyboardButton(text="????????", callback_data=f"help+1"),
                InlineKeyboardButton(
                    text="?????? ???? ?????????? +",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="?????", url=f"https://t.me/{SUPPORT_GROUP}"
                ),
                InlineKeyboardButton(
                    text="???????", url=f"https://t.me/{UPDATES_CHANNEL}"
                ),
            ],
            [
                InlineKeyboardButton("??? ??? ", url=f"{SOURCE_CODE}"),
                InlineKeyboardButton(
                    "????????", url="https://t.me/hamaari_paltan"
                ),
            ],
        ]
    else:
        button = [
            [
                InlineKeyboardButton(
                    text="????????????????", callback_data=f"help+{pos-1}"
                ),
                InlineKeyboardButton(
                    text="???????? ??", callback_data=f"help+{pos+1}"
                ),
            ],
        ]
    return button


@Client.on_message(filters.command("reload") & filters.group & ~filters.edited)
@authorized_users_only
async def admincache(client, message: Message):
    await message.reply_photo(
        photo=f"{vincenzo}",
        caption="? **??? ??s?????? s????ss?????!!**\n\n **??????s?s ??????? s????ss?????**",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="?? ?????", url=f"t.me/{OWNER}")],
                [
                    InlineKeyboardButton(
                        text="??????????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                    InlineKeyboardButton(
                        text="??????????????", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
                [
                    InlineKeyboardButton("^ ?????? ?????? ^", url=f"{SOURCE_CODE}"),
                    InlineKeyboardButton(
                        "????????", url="https://t.me/hamaari_paltan"
                    ),
                ],
            ]
        ),
    )


@Client.on_message(filters.command("help") & ~filters.private & ~filters.channel)
async def ghelp(_, message: Message):
    await message.reply_text(
        """
**????????????????**
      
**=>> PLAY SONG**
      
• /play (song name) - TO PLAY THE REQUESTED SONG..
• /ytplay (SONG NAME) - TO PLAY THE REQUESTED SONG VIA YOUTUBE.
• /yt (SONG NAME) - TO PLAY THE REQUESTED SONG FROM YT.
• /p (SONG NAME) - TO PLAY THE REQUESTED SONG VIA YOUTUBE.
• /lplay - TO PLAY THE SONG YOU REPLY FORM GC....
• /player: GO TO PLAYER SETTINGS MENU....
• /skip: SKIPS THE PLAYING SONG..
• /pause: PAUSES STREAMING....
• /resume: RESUMES STREAMING...
• /end: STOPS STREAMING....
• /current: SHOW THE CURRENTLY PLAYING TRACK
• /playlist: SHOWS THE LIST OF REQUESTED SONGS
      
SOME COMMANDS THAT CAN BE USED INSTEAD OF /player /skip /pause /resume  /end  **ONLY FOR GROUP ADMINS**
      
**==>>Download SONG**
      
• /song [SONG NAME]: DOWNLOAD SONG AUDIO FROM YT..
**=>> CHANNEL Music Play ??**
      
FOR GROUP ADMINS ONLY:
      
• /cplay (SONG NAME) - PLAYS THE REQUESTED SONG
• /cplaylist - SHOW CURRENT PLAYLIST..
• /cccurrent - SHOWS WHAT IS PLAYING
• /cplayer - SHOWS CURRENT SONG PLAYER...
• /cpause - PAUSES STREAMING......
• /cresume - RESUMES STREAMING....
• /cskip - SKIPS CURRENTLY PLAYING SONG.....
• /cend - ENDS STREAMING......
• /userbotjoinchannel - ASSISTANT BOT JOINS THE CHAT..""",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="?????", url=f"t.me/{OWNER}")],
                [
                    InlineKeyboardButton(
                        text="?????", url=f"https://t.me/{SUPPORT_GROUP}"
                    ),
                    InlineKeyboardButton(
                        text="???????", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
                [
                    InlineKeyboardButton("?? ??? ??? ??", url=f"{SOURCE_CODE}"),
                    InlineKeyboardButton(
                        "?? ????????", url="https://trakteer.id/kenkansaja/tip"
                    ),
                ],
            ]
        ),
    )
