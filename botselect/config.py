import concurrent.futures
import configparser
import pathlib
import logging
import re

import semver

SEMVER = semver.VersionInfo(
    major=0,
    minor=0,
    patch=1,
)
VERSION = str(SEMVER)

EXECUTOR = concurrent.futures.ThreadPoolExecutor()

PROJECT_DIR = pathlib.Path(__file__).parent.parent
NEEDS_WRITE = False
CONFIG_FILENAME = 'botselect.ini'
CONF = configparser.ConfigParser()
CONF.read(CONFIG_FILENAME)


def write():
    with open(CONFIG_FILENAME, 'w') as file_pointer:
        CONF.write(file_pointer)


SEC_DEFAULT = "default"
SEC_IMAGES = "images"
SEC_DEBUG = "debug"

# Configurable Stuff
if not CONF.has_section(SEC_DEFAULT):
    CONF.add_section(SEC_DEFAULT)

SHEET_URL = CONF.get(SEC_DEFAULT, "sheet_url")
# Parse out the spreadsheet ID
pattern1 = r".*/spreadsheets/d/([\w\-]+)/.*"
pattern2 = r"^([\w\-]+)$"
match = re.match(pattern1, SHEET_URL) or re.match(pattern2, SHEET_URL)
SHEET_ID = -1
if match:
    SHEET_ID = match.group(1)
if not match:
    print("Couldn't parse spreadsheet ID from URL: %s", SHEET_URL)

API_KEY = CONF.get(SEC_DEFAULT, "api_key")

LOG_LEVEL = CONF.getint(SEC_DEBUG, "loglevel", fallback=logging.INFO)
CACHE_FILE = CONF.get(SEC_DEFAULT, "cache_file", fallback="cache.json")
USE_QUICKCONNECT = CONF.getboolean(
    SEC_DEFAULT, "use_quickconnect", fallback=False)

# Debug Options
EQ_WINDOW_TITLE_REGEX = CONF.get(
    SEC_DEBUG, "EQ_WINDOW_TITLE_REGEX", fallback=None)

IMG_EULA_BUTTON = CONF.get(
    SEC_IMAGES, "eula_accept",
    fallback=r"images\1_eula_accept.png")
IMG_SOE_LOGO = CONF.get(
    SEC_IMAGES, "soe_logo",
    fallback=r"images\2_soe_logo.png")
IMG_LOGIN_BUTTON1 = CONF.get(
    SEC_IMAGES, "login_button_deselected",
    fallback=r"images\3_login_deselected.png")
IMG_LOGIN_BUTTON2 = CONF.get(
    SEC_IMAGES, "login_button_selected",
    fallback=r"images\3_login_selected.png")
IMG_LOGIN_USER_FIELD = CONF.get(
    SEC_IMAGES, "login_user_field",
    fallback=r"images\4_login_user_field.png")
IMG_LOGIN_PASSWORD_FIELD = CONF.get(
    SEC_IMAGES, "login_password_field",
    fallback=r"images\5_login_password_and_button.png")
IMG_LOGIN_QUICKCONNECT = CONF.get(
    SEC_IMAGES, "login_quickconnect_button",
    fallback=r"images\6_login_quickconnect.png")
