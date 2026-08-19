import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

MAIN_HOST = "https://ridenow3.ct.ms"

ADMIN_AUTH = {
    "login": "ridenow@test.ru",
    "password": "u8MV9F"
}

CLIENT_ORG_LIST = ["d41a9561-3d2d-40a1-99b1-b0ee013eaad3", # A4
                   "f6477857-4eda-476c-bcf6-ae7500decd0f", # A3
                   "01b1ddda-35b5-4360-a5c5-ad5e00746090", # A2
                   "59d81c7d-e06f-479f-8562-ab4e00fba740"] # A1

NIGHT_WATCH_ORG = "d2a478e0-bca2-4cfc-a830-b22e011a15ec"
NIGHT_WATCH_EXTEND_ORG = "0c5cff7c-b324-4714-b633-b22f0132777d"

# SQL Replica main
REPL_DB = os.getenv("REPL_DB")
REPL_USER = os.getenv("REPL_USER")
REPL_HOST = os.getenv("REPL_HOST")
REPL_PASS = os.getenv("REPL_PASS")
REPL_PORT = os.getenv("REPL_PORT")

# SQL TECH
TECH_DB = os.getenv("TECH_DB")
TECH_USER = os.getenv("TECH_USER")
TECH_HOST = os.getenv("TECH_HOST")
TECH_PASS = os.getenv("TECH_PASS")
TECH_PORT = os.getenv("TECH_PORT")

# CT Mobility settings
CT_API_KEY_CAR_CONTROL = os.getenv("CT_API_KEY_CAR_CONTROL")
CT_MAIN_HOST = os.getenv("CT_MAIN_HOST")

# Telegram Bot Token
CAR_BOT_TOKEN = os.getenv("CAR_BOT_TOKEN")

# Admin session id for /admin/events/customer requests
CARTREK_SESSION_ID = os.getenv("CARTREK_SESSION_ID")

# Admin sessid cookie (set-cookie: sessid=...)
CARTREK_SESSID = os.getenv("CARTREK_SESSID")

