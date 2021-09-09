import os
from os import getenv

from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

que = {}
SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN")
BOT_NAME = getenv("BOT_NAME")
ARQ_API_KEY = getenv("ARQ_API_KEY", None)
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "our_SECRET_SOCIETY")
BG_IMAGE = getenv("BG_IMAGE", "https://telegra.ph/file/744ec1f5f15768fd3cc0b.jpg")
admins = {}
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_USERNAME = getenv("BOT_USERNAME")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "VINCENZO_MUSIC_BOT_ASSISTANT")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "our_SECRET_SOCIETY")
PROJECT_NAME = getenv("PROJECT_NAME", "VINCENZO_MUSIC_BOT")
OWNER = getenv("OWNER", "@koii_nhi_apnaa")
SOURCE_CODE = getenv("SOURCE_CODE", "github.com/vincenzo-op/VINCENZO_MUSIC_BOT")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "7"))
PMPERMIT = getenv("PMPERMIT", None)
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ !").split())

SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))
vincenzo = getenv("vincenzo", "https://telegra.ph/file/744ec1f5f15768fd3cc0b.jpg")
