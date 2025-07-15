import os
import json
from math import floor
from enum import Enum

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/script.projects"  # Don't forget to enable the API both on the Google Console AND on the Apps Scripts home page
]

FOLDER_ID_TAREA_DE_TRADUCCION = "1cJp6GuDk_LT766aVgZae9ER962VU2GlH"
DATETIME_FORMAT = '%b %d %Y %I:%M%p'
LOGGER_FORMAT = '%(levelname)s : %(asctime)s %(message)s'
HOME = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
CATEGORY_COLUMN_SPREADSHEET_ID = "1EGhgsdl2MSI2-mQ6ilkTaLFGVtjtmujU7mkCqZwuL6Y"

PACKET_SIZE = 6
R_MAX = 2

with open("../data/flores.eng-spa.dev") as f:
    DEV = f.readlines()
    DEV = [
        DEV[x:x + PACKET_SIZE] for x in range(0, len(DEV), PACKET_SIZE)
    ]

with open("../data/flores.eng-spa.dev") as f:
    DEVTEST = f.readlines()
    DEVTEST = [
        DEVTEST[x:x + PACKET_SIZE] for x in range(0, len(DEVTEST), PACKET_SIZE)
    ]

with open("../data/vocabulario_flores_plus.json") as f:
    VOCAB_FLORES_PLUS = json.loads(f.read())

R = 120
NUMBER_OF_SENTENCES_FROM_DEV_SET = floor(len(DEV) * .18)
n = len(DEVTEST)

COLOR_GOOD = {
    "red": 68 / 255,
    "green": 170 / 255,
    "blue": 153 / 255,
}

COLOR_MINOR = {
    "red": 221 / 255,
    "green": 204 / 255,
    "blue": 119 / 255,
}

COLOR_MAJOR = {
    "red": 204 / 255,
    "green": 102 / 255,
    "blue": 119 / 255,
}

COLOR_CRITICAL = {
    "red": 170 / 255,
    "green": 68 / 255,
    "blue": 153 / 255,
}

COLOR_IGNORE = {
    "red": 136 / 255,
    "green": 204 / 255,
    "blue": 238 / 255,
}

COLOR_VOCAB = {
    "red": 51 / 255,
    "green": 34 / 255,
    "blue": 136 / 255,
}


class Stage(str, Enum):
    FIRST_TRANSLATION = 'FIRST_TRANSLATION'
    FIRST_REVISION = 'FIRST_REVISION'
    SECOND_TRANSLATION = 'SECOND_TRANSLATION'
    SECOND_REVISION = 'SECOND_REVISION'
    TRANSLATION_COMPLETE = 'TRANSLATION_COMPLETE'
