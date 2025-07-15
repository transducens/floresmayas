import os.path
import json
from constants import SCOPES, COLOR_VOCAB, PACKET_SIZE
from Levenshtein import distance
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from icecream import ic


def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    elif not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def minLev(w, s):
    sent = s.split()
    min_distance = distance(w, sent[0])
    min_lev_word = sent[0]
    for word in sent:
        if distance(w, word) < min_distance:
            min_distance = distance(w, word)
            min_lev_word = word
    return min_lev_word


def get_text_format_runs(text, tokenised_text, vocab):
    vocab_words = [
        minLev(word, text) for word in tokenised_text if word in vocab
    ]
    idx_runs = [text.index(word) for word in vocab_words]
    idx_runs = [
        (idx, idx + len(word)) for idx, word in zip(idx_runs, vocab_words)
    ]
    runs = [
        (
            {
                "startIndex": idx[0],
                "format": {
                    "foregroundColorStyle": {
                        "rgbColor": COLOR_VOCAB
                    },
                    "bold": True
                }
            },
            {
                "startIndex": idx[1],
                "format": {
                    "foregroundColorStyle": {
                        "rgbColor": {
                            "red": 0,
                            "green": 0,
                            "blue": 0
                        }
                    },
                    "bold": False
                }
            }
        ) for idx in idx_runs
    ]
    runs = [run for pair in runs for run in pair]
    return runs


def get_users(users_filename: str) -> dict:
    with open(users_filename) as f:
        return json.loads(f.read())


def is_ready_packet(id: str, creds: object) -> bool:
    # if id == '':
    #     return False
    service = build("sheets", "v4", credentials=creds)
    last_sheet_name = service.spreadsheets().get(spreadsheetId=id).execute()['sheets'][-1]['properties']['title']
    results = (
        service.spreadsheets().get(
            spreadsheetId=id,
            includeGridData=True,
            ranges=[f"{last_sheet_name}!B{PACKET_SIZE + 2}"]
        ).execute()
    )

    rgb_color = (
        results['sheets'][-1]
        ['data'][0]
        ['rowData'][0]
        ['values'][0]
        ['effectiveFormat']
        ['backgroundColorStyle']
        ['rgbColor']
    )

    return len(rgb_color.keys()) == 1 and rgb_color.get('green') == 1


def is_complete_translation(id: str, creds: object) -> bool:
    service = build("sheets", "v4", credentials=creds)
    data = service.spreadsheets().values().get(
        spreadsheetId=id,
        range=(f"G2:G{PACKET_SIZE + 2}")
    ).execute()
    data = [value[0] for value in data['values']]

    return len([value for value in data if value == "Correcta"]) == len(data)

if __name__ == "__main__":

    print(is_ready_packet("1mBKH7xlPt6F9WvXyTcPyf5JQu5NeEA6wMGBCit9QAFg", authenticate()))