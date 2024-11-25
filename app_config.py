import os

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
REPL_DB = "ridenow"
REPL_USER = "user_rep"
REPL_HOST = "138.201.48.57"
REPL_PASS = "L5p%6E$bDirK"
REPL_PORT = 5432

# SQL Procedures DB
PROC_DB = "ridenow_procedures"
PROC_USER = "postgres"
PROC_HOST = "138.201.48.57"
PROC_PASS = "D3ZNPy9NeQxAYn"
PROC_PORT = 5433
