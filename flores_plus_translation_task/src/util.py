import os
import os.path
import json
import smtplib
import ssl
from math import sqrt, floor
from typing import List, Union
from email.message import EmailMessage
from Levenshtein import distance
from constants import SCOPES, COLOR_VOCAB, PACKET_SIZE, FOLDER_ID_TAREA_DE_TRADUCCION
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

def get_c(R, k, n, t):
    if n == t:
        return R - k

    return (R - k) / (2 * (sqrt(n) - sqrt(t)))


def get_r_max(c, t):
    return floor(c / sqrt(t))


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


def get_translation_ids(creds: object, rev_id: str) -> list:
    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets().get(spreadsheetId=rev_id).execute()['sheets']
    sheet_title = sheets[-1]['properties']['title']
    values = service.spreadsheets().values().get(spreadsheetId=rev_id, range=f"{sheet_title}!A1:N{PACKET_SIZE + 1}").execute()['values']
    if len(sheets) == 1:
        values = [value[0] for value in values[1:]]
        return values, []

    tra_values = [value for value in values[1:] if len(value) != 14]
    rev_values = [value for value in values[1:] if len(value) == 14]

    tra_values = [value[0] for value in tra_values]
    rev_values = [value[0] for value in rev_values]

    return tra_values, rev_values


def generate_config(langs: list, n_packets: int) -> dict:
    config = {
        lang: {
            "translators": {},
            "revisors": {},
            "packets": {
                i: None for i in range(n_packets)
            },
        } for lang in langs
    }

    return config


def remove_permissions(creds, state: dict) -> list:
    doc_ids = []
    for lang in state:
        for packet in state[lang]['packets']:
            for worker in 'tra_id', 'rev_id':
                if state[lang]['packets'][packet] and state[lang]['packets'][packet][worker]:
                    doc_ids.append(state[lang]['packets'][packet][worker])
        if state[lang].get("vocab_id") is not None:
            doc_ids.append(state[lang].get("vocab_id"))

    workers_to_remove = []
    for lang in state:
        for worker in state[lang]['inactive_translators'].keys():
            workers_to_remove.append(worker)

    service = build("drive", "v3", credentials=creds)
    for doc_id in doc_ids:
        results = service.permissions().list(fileId=doc_id, fields="permissions").execute()
        for permission in results['permissions']:
            if permission['emailAddress'] in workers_to_remove:
                service.permissions().delete(
                    fileId=doc_id,
                    permissionId=permission['id']
                ).execute()

    return workers_to_remove


def get_lang_folder(creds, lang: str) -> str:

    service = build("drive", "v3", credentials=creds)
    q = f"mimeType='application/vnd.google-apps.folder' and name = '{lang}' and parents in '{FOLDER_ID_TAREA_DE_TRADUCCION}'"
    response = service.files().list(q=q).execute()
    if len(response['files']) == 0:
        return ""
    return response['files'][0]['id']


def create_lang_folder(creds, lang: str) -> str:
    service = build("drive", "v3", credentials=creds)
    folder_metadata = {
        "name": lang,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [FOLDER_ID_TAREA_DE_TRADUCCION],
    }
    parent_folder = (
        service
        .files()
        .create(body=folder_metadata, fields="id")
        .execute()
    )
    parent_folder = parent_folder.get('id')


def get_vocab_from_sheet(creds, doc_id: str) -> dict:
    service = build("sheets", "v4", credentials=creds)
    vocab = service.spreadsheets().values().get(
        spreadsheetId=doc_id,
        range="A2:C"
    ).execute()
    vocab = vocab['values']
    vocab = {
        row[0]: {
            'def': row[0] if len(row) > 2 else "",
            'notes': row[0] if len(row) > 3 else ""
        } for row in vocab
    }
    return vocab


# def get_spacy_vocab_and_tokens(lang: str, lang_vocab: dict, spa: list):

#     spa_tokens = []

#     vocab = []
#     nlp = spacy.load("es_core_news_sm")
#     disabled = ["parser", "ner", "textcat", "custom"]
#     pos_tags = ["NOUN", "PROPN", "VERB", "ADJ", "ADV"]

#     for idx, value in enumerate(spa):
#         tokens = [
#             token.lemma_ if token.pos_ in pos_tags else token.text
#             for doc in nlp.pipe([value], disable=disabled)
#             for token in doc
#         ]
#         spa_tokens.append(tokens)
#         cell_vocab = [
#             token for token in tokens if token in lang_vocab.keys()
#         ]
#         cell_vocab = [
#             token + f": {lang_vocab.get(token).get('def')}\n" for token in cell_vocab
#         ]
#         cell_vocab = sorted(list(set(cell_vocab)))
#         cell_vocab = "".join(cell_vocab)
#         vocab.append(cell_vocab)

    # vocab : list of strings: Each string goes like word:\nword:\n etc
    # spa_tokens : list of lists. Each sentence is tokenised
    return vocab, spa_tokens


def get_vocab_and_spa_tokens(lang_vocab: dict, packet_idx: int):
    spa_tokens = []
    vocab = []
    for filename in os.listdir(f"../data/tokens/{packet_idx}"):
        with open(f"../data/tokens/{packet_idx}/{filename}") as f:
            spa_tokens.append(f.readlines())

    for idx, line in enumerate(spa_tokens):
        line = [token.strip() for token in line]
        line = [token for token in line if lang_vocab.get(token) and
                lang_vocab[token]['def']]
        line_vocab = list(set(line))
        line_vocab = [token for token in line_vocab if lang_vocab.get(token)
                      and lang_vocab.get(token).get('def')]
        line_vocab = [f"{token}: {lang_vocab[token]['def']} \n" for token in line_vocab]
        line_vocab = "".join(line_vocab)
        vocab.append(line_vocab)
        spa_tokens[idx] = line
    return vocab, spa_tokens

def update_sheet_vocabulary(creds, state: dict, lang: str) -> None:
    with open(f"../data/{lang}/vocab.json") as f:
        lang_vocab = json.loads(f.read())

    service = build("sheets", "v4", credentials=creds)
    packets = [packet for packet in state[lang]['packets'] if state[lang]['packets'][packet] is not None and state[lang]['packets'][packet]['stage'] != "TRANSLATION_COMPLETE"]

    for packet in packets:
        fileId = state[lang]['packets'][packet]['tra_id']
        packet_idx = state[lang]['packets'][packet]['packet_idx']
        spa = service.spreadsheets().values().get(
            spreadsheetId=fileId,
            range="C2:C"
        ).execute()
        spa = [sent[0] for sent in spa['values']]
        vocab, spa_tokens = get_vocab_and_spa_tokens(lang_vocab, packet_idx)
        if len([v for v in vocab if v]) > 0: # make sure there is at least one vocab term with a definition
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                        "range": "D2:D",
                        "majorDimension": "COLUMNS",
                        "values": [
                            vocab
                        ]
                    }
                ]
            }
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=fileId,
                body=body
            ).execute()

        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "startRowIndex": idx + 1,
                            "endRowIndex": idx + 2,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3,
                        },
                        "cell": {
                            "textFormatRuns": get_text_format_runs(spa[idx], spa_tokens[idx], list(lang_vocab.keys()))
                        },
                        "fields": "textFormatRuns.format.foregroundColorStyle, textFormatRuns.format.bold"
                    }
                } for idx, _ in enumerate(spa)
            ]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=fileId,
            body=body
        ).execute()

def send_email_notification(recipients: Union[List[str], str], message: str, subject: str) -> None:
    sender_email = os.getenv("EMAIL_ADRESS")
    email_password = os.getenv("EMAIL_PASSWD")
    receiver_email = ', '.join(recipients)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"FLORES+ Mayas <{sender_email}>"
    msg['To'] = ', '.join(recipients) if type(recipients) == list else recipients
    msg.set_content(message)

    smtp_server = "smtp.gmail.com"
    port = 465

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, email_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def protect_packet_sheets(ssheets_ids: list, creds) -> None:
    service = build("sheets", "v4", credentials=creds)
    for ss in ssheets_ids:
        response = service.spreadsheets().get(
            spreadsheetId=ss,
            fields="sheets(protectedRanges(protectedRangeId),properties(sheetId))"
            ).execute()

        # Collect all protectedRangeIds into a list of delete requests
        requests = []
        for sheet in response.get('sheets', []):
        # Check if the sheet has any protected ranges
            if 'protectedRanges' in sheet:
                for pr in sheet['protectedRanges']:
                    requests.append({
                        "deleteProtectedRange": {
                            "protectedRangeId": pr['protectedRangeId']
                        }
                    })
            new_protection_request = {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                        "sheetId": sheet['properties']['sheetId']
                        },
                        "description": "Master Lock",
                        "warningOnly": False,
                        "editors": {
                            "users": ["and_lou@gcloud.ua.es"]
                        }
                    }
                }
            }
            requests.append(new_protection_request)
        if requests:
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=ss,
                body=body
            ).execute()
            print("All previous protections removed. New protection applied.")
        else:
            print("No changes needed.")

def __main__():
    creds = authenticate()
    ssheets = ["1eutIMHCgvhLUk3v7C56_Ds1bOQV9vu5teMFoo7lPPn8"]

    protect_packet_sheets(ssheets, creds)

if __name__ == "__main__":
    __main__()
