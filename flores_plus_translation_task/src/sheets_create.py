import os
import spacy
import datetime
from constants import *
from util import *
from random import shuffle
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def create_translation_spreadsheet(
    creds,
    sents,
    lang_code,
    title,
    tra_email,
    rev_email,
    packet_idx,
):

    ids = [row.split('\t')[0] for row in sents]
    eng = [row.split('\t')[1] for row in sents]
    spa = [row.split('\t')[2] for row in sents]
    spa_tokens = []

    vocab = []
    nlp = spacy.load("es_core_news_sm")
    disabled = ["parser", "ner", "textcat", "custom"]
    pos_tags = ["NOUN", "PROPN", "VERB", "ADJ", "ADV"]

    with open(f"../data/{lang_code}/vocab.json") as f:
        lang_vocab = json.loads(f.read())

    for idx, value in enumerate(spa):
        tokens = [
            token.lemma_ if token.pos_ in pos_tags else token.text
            for doc in nlp.pipe([value], disable=disabled)
            for token in doc
        ]
        spa_tokens.append(tokens)
        cell_vocab = [
            token for token in tokens if token in lang_vocab.keys()
        ]
        cell_vocab = [
            token + f": {lang_vocab.get(token).get('def')}\n\n" for token in cell_vocab
        ]
        cell_vocab = "".join(cell_vocab)
        vocab.append(cell_vocab)

    # Create translation sheet
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = {
        "properties": {
            "title": title
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": "traducción",
                }
            }
        ],
    }
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    id = spreadsheet.get('spreadsheetId')

    # Create permissions for translator
    drive_service = build("drive", "v3", credentials=creds)

    body = {
        "type": "user",
        "role": "writer",
        "emailAddress": tra_email
    }

    drive_service.permissions().create(fileId=id, body=body).execute()

    # Put all the data on the sheet
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "A1:I1",
                "values": [
                    [
                        "Id",
                        "Inglés",
                        "Español",
                        "Vocabulario",
                        "Traducción"
                    ]
                ],
            },
            {
                "range": "A2:A",
                "majorDimension": "COLUMNS",
                "values": [
                    ids
                ]
            },
            {
                "range": "B2:B",
                "majorDimension": "COLUMNS",
                "values": [
                    eng
                ]
            },
            {
                "range": "C2:C",
                "majorDimension": "COLUMNS",
                "values": [
                    spa
                ]
            },
            {
                "range": "D2:D",
                "majorDimension": "COLUMNS",
                "values": [
                    vocab
                ]
            },
            {
                "range": f"A{len(spa) + 2}",
                "values": [["Completado"]]
            },
            {
                "range": f"B{len(spa) + 3}",
                "values": [["No puedes marcar la tarea como «Completada» si hay celdas en blanco, celdas que requieran de una selección o celdas que indiquen un problema con la selección."]]
            }
        ],
    }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=id,
        body=body
    ).execute()

    # Format the data
    body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 1,
                        "endRowIndex": 1000
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy",
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": len(spa) + 2,
                    },
                    "properties": {
                        "pixelSize": 300,
                    },
                    "fields": "pixelSize",
                }
            },
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": 0,
                        },
                        "description": "Id y lenguas originales",
                        "unprotectedRanges": [
                            {
                                "sheetId": 0,
                                "startRowIndex": 1,
                                "endRowIndex": len(spa) + 1,
                                "startColumnIndex": 4,
                                "endColumnIndex": 5,
                            },
                            {
                                "startRowIndex": len(spa) + 1,
                                "endRowIndex": len(spa) + 2,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "editors": {
                            "users": [
                                "and_lou@gcloud.ua.es",
                            ]
                        }
                    }
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": len(spa) + 1,
                        "endRowIndex": len(spa) + 2,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "dataValidation": {
                            "condition": {
                                "type": "BOOLEAN",
                            },
                            "strict": True
                        },
                    },
                    "fields": "dataValidation.condition"
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": len(spa) + 1,
                                "endRowIndex": len(spa) + 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{len(spa) + 2};TRUE);NOT(OR(ARRAYFORMULA(ISBLANK($E2:$E{len(spa) + 1})))))'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0,
                                    "green": 1,
                                    "blue": 0
                                }
                            }
                        }
                    },
                    "index": 0
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": len(spa) + 1,
                                "endRowIndex": len(spa) + 2,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{len(spa) + 2};TRUE);OR(ARRAYFORMULA(ISBLANK($E2:$E{len(spa) + 1}))))'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1,
                                    "green": 0,
                                    "blue": 0
                                }
                            }
                        }
                    },
                    "index": 1
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": len(spa) + 2,
                        "endRowIndex": len(spa) + 3,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "foregroundColorStyle": {
                                    "rgbColor": {
                                        "red": 1,
                                        "green": 1,
                                        "blue": 1
                                    }
                                }
                            }
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.foregroundColorStyle"
                }
            },
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": len(spa) + 2,
                                "endRowIndex": len(spa) + 3,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{len(spa) + 2};TRUE);OR(ARRAYFORMULA(ISBLANK($E2:$E{len(spa) + 1}))))'}
                            },
                            "format": {
                                "textFormat": {
                                    "foregroundColorStyle": {
                                        "rgbColor": {
                                            "red": 0,
                                            "green": 0,
                                            "blue": 0
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "index": 3
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": len(spa) + 1,
                        "endRowIndex": len(spa) + 2,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True}
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            }
        ] + [
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
        spreadsheetId=id,
        body=body
    ).execute()

    service = build("drive", "v3", credentials=creds)

    # Create folder if no folder exists for language
    q = f"mimeType='application/vnd.google-apps.folder' and parents in '{FOLDER_ID_TAREA_DE_TRADUCCION}'"
    response = (service.files().list(q=q).execute())
    files = response['files']
    files = [file for file in files if file.get('name') == lang_code]
    if len(files) == 0:
        folder_metadata = {
            "name": lang_code,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": ["1cJp6GuDk_LT766aVgZae9ER962VU2GlH"],
        }
        parent_folder = (
            service
            .files()
            .create(body=folder_metadata, fields="id")
            .execute()
        )
        parent_folder = parent_folder.get('id')
    else:
        parent_folder = [
            obj for obj in response['files'] if obj['name'] == lang_code
        ]
        parent_folder = parent_folder[0].get('id')

    # Move translation spreadsheet into corresponding folder
    try:
        file = service.files().get(
            fileId=id, fields="parents"
        ).execute()
        previous_parents = ",".join(file.get("parents"))
        file = (
            service.files()
            .update(
                fileId=id,
                addParents=parent_folder,
                removeParents=previous_parents,
                fields="id, parents",
            )
        ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

    return {
        "tra_id": id,
        "rev_id": None,
        "title": title,
        "created": datetime.datetime.now().strftime(DATETIME_FORMAT),
        "last_stage_update": datetime.datetime.now().strftime(DATETIME_FORMAT),
        "translator": tra_email,
        "revisor": rev_email,
        "stage": Stage.FIRST_TRANSLATION,
        "packet_idx": packet_idx
    }


def create_revision_spreadsheet(creds, lang_code, title, packet):
    tra_id = packet['tra_id']
    sheets_service = build("sheets", "v4", credentials=creds)

    # Get protected range id and lock first translation sheet
    protected_range_id = (
        sheets_service.spreadsheets().get(spreadsheetId=tra_id).execute()
    )
    protected_range_id = (
        protected_range_id
        ['sheets'][0]
        ['protectedRanges'][0]
        ["protectedRangeId"]
    )

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=tra_id,
        body={
            "requests": [
                {
                    "updateProtectedRange": {
                        "protectedRange": {
                            "protectedRangeId": protected_range_id,
                            "unprotectedRanges": []
                        },
                        "fields": "unprotectedRanges"
                    }
                }
            ]
        }
    ).execute()

    # Copy spreadsheet from translation to turn it into revision
    drive_service = build("drive", "v3", credentials=creds)

    body = {
        'name': f'{title}_rev',
    }
    file = drive_service.files().copy(fileId=tra_id, body=body).execute()
    rev_id = file['id']

    body = {
        "type": "user",
        "role": "writer",
        "emailAddress": packet['revisor']
    }

    results = (
        drive_service.permissions().create(
            fileId=rev_id,
            body=body
        ).execute()
    )

    # copy validation column from external file
    results = (
        sheets_service.spreadsheets().sheets().copyTo(
            spreadsheetId=CATEGORY_COLUMN_SPREADSHEET_ID,
            sheetId=0,
            body={"destinationSpreadsheetId": rev_id}
        ).execute()
    )
    copy_sheet_id = results['sheetId']

    # get row index of completion checkbox
    checkbox_row_index = (
        sheets_service
        .spreadsheets()
        .values()
        .batchGet(spreadsheetId=tra_id, ranges="A:A")
        .execute()['valueRanges'][0]['values']
    )
    checkbox_row_index = len(checkbox_row_index)

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "F1:I1",
                "values": [
                    [
                        "Categoría",
                        "Estado",
                        "Comentario",
                        "Fila válida",
                    ]
                ],
            },
            {
                "range": f"B{checkbox_row_index}",
                "values": [[False]]
            },
        ],
    }

    sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=rev_id,
        body=body
    ).execute()

    body = {
        "requests": [
            # Crear columna de categorías
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 5,
                        "endColumnIndex": 6,
                    },
                    "fields": "dataValidation.condition",
                    "cell": {
                        "dataValidation": {
                            "strict": True,
                            "showCustomUi": True,
                            "inputMessage": "Seleccione una categoría de error dentro de las posibles opciones",
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": "Gramática"},
                                    {"userEnteredValue": "Puntuación"},
                                    {"userEnteredValue": "Ortografía"},
                                    {"userEnteredValue": "Mayúsculas"},
                                    {"userEnteredValue": "Adición/Omisión"},
                                    {"userEnteredValue": "Traducción errónea"},
                                    {"userEnteredValue": "Traducción no natural"},
                                    {"userEnteredValue": "Texto no traducido"},
                                    {"userEnteredValue": "Registro"},
                                ]
                            }
                        }
                    }
                }
            },

            # Crear columna de severidad
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "fields": "dataValidation.condition",
                    "cell": {
                        "dataValidation": {
                            "strict": True,
                            "showCustomUi": True,
                            "inputMessage": "Seleccione una categoría de severidad dentro de las posibles opciones",
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": "Correcta"},
                                    {"userEnteredValue": "Error menor"},
                                    {"userEnteredValue": "Error mayor"},
                                    {"userEnteredValue": "Error crítico"},
                                ]
                            }
                        }
                    }
                }
            },

            # Hacer que las columnas de categoría y severidad sean más angostas
            {
                "updateDimensionProperties": {
                    "range": {
                        "dimension": "COLUMNS",
                        "startIndex": 5,
                        "endIndex": 7,
                    },
                    "properties": {
                        "pixelSize": 100,
                    },
                    "fields": "pixelSize",
                }
            },

            # Regla de formato: fila correcta
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": 0,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=AND(EQ($G2;"Correcta");EQ($F2;"");EQ($H2;""))'}
                            },
                            "format": {
                                "backgroundColor": COLOR_GOOD
                            }
                        }
                    },
                    "index": 0
                }
            },

            # Regla de formato: error menor
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": 4,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=EQ(G2;"Error menor")'}
                            },
                            "format": {
                                "backgroundColor": COLOR_MINOR
                            }
                        }
                    },
                    "index": 1
                }
            },

            # Regla de formato: error mayor
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": 4,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=EQ(G2;"Error mayor")'}
                            },
                            "format": {
                                "backgroundColor": COLOR_MAJOR
                            }
                        }
                    },
                    "index": 2
                }
            },

            # Regla de formato: error crítico
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": 4,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=EQ(G2;"Error crítico")'}
                            },
                            "format": {
                                "backgroundColor": COLOR_CRITICAL
                            }
                        }
                    },
                    "index": 3
                }
            },

            # Regla de formato: casilla marcada «correcta» pero hay categoría de error o comentario
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": 6,
                                "endColumnIndex": 7,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=AND(EQ($G2;"Correcta");NOT(AND(EQ($F2;"");EQ($H2;""))))'}
                            },
                            "format": {
                                "backgroundColor": COLOR_CRITICAL
                            }
                        }
                    },
                    "index": 4
                }
            },

            # Cambiar el título a la hoja
            {
                "updateSheetProperties": {
                    "properties": {
                        "title": "1ra revisión",
                    },
                    "fields": "title",
                }
            },

            # Protección para que el revisor solo pueda tocar la categoría, severidad y el comentario
            {
                "updateProtectedRange": {
                    "protectedRange": {
                        "protectedRangeId": protected_range_id,
                        "description": "ID, lenguas originales y traducción",
                        "unprotectedRanges": [
                            {
                                "sheetId": 0,
                                "startRowIndex": 1,
                                "endRowIndex": checkbox_row_index - 1,
                                "startColumnIndex": 5,
                                "endColumnIndex": 8,
                            },
                            {
                                "startRowIndex": checkbox_row_index - 1,
                                "endRowIndex": checkbox_row_index,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "editors": {
                            "users": [
                                "and_lou@gcloud.ua.es",
                            ]
                        }
                    },
                    "fields": "description, unprotectedRanges.startColumnIndex, unprotectedRanges.endColumnIndex",
                }
            },

            # Copiar desde un archivo externo la columna de categoría para contar con múltiples opciones simultáneas
            {
                "copyPaste": {
                    "source": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "destination": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "startColumnIndex": 5,
                        "endColumnIndex": 6,
                    },
                    "pasteType": "PASTE_NORMAL",
                }
            },

            # Borrar la hoja que contenía la columna de categoría con múltiples opciones simultáneas
            {
                "deleteSheet": {
                    "sheetId": copy_sheet_id,
                },
            },

            # Validación de cada fila
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "endRowIndex": checkbox_row_index - 1,
                        "startColumnIndex": 8,
                        "endColumnIndex": 9,
                    },
                    "cell": {
                        "userEnteredValue": {
                            "formulaValue": '=AND(NOT(EQ($G2;""));OR(AND(EQ($F2;"");EQ($H2;"");EQ($G2;"Correcta"));NOT(OR(EQ($F2;"");EQ($H2;"");EQ($G2;"Correcta")))))',
                        },
                    },
                    "fields": "userEnteredValue"
                }
            },

            # Ocultar la columna de validación
            {
                "updateDimensionProperties": {
                    "properties": {
                        "hiddenByUser": True,
                    },
                    "fields": "hiddenByUser",
                    "range": {
                        "sheetId": 0,
                        "dimension": "COLUMNS",
                        "startIndex": 8,
                        "endIndex": 9,
                    }
                }
            },

            # Validar casilla de Completado: válida
            {
                "updateConditionalFormatRule": {
                    "index": 5,
                    "sheetId": 0,
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": checkbox_row_index - 1,
                                "endRowIndex": checkbox_row_index,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f"=AND($B{checkbox_row_index};AND(ARRAYFORMULA($I2:I{checkbox_row_index - 1})))"}
                            },
                            "format": {
                                "backgroundColorStyle": {
                                    "rgbColor": {
                                        "red": 0,
                                        "green": 1,
                                        "blue": 0
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # Validar casilla de Completado: no válida
            {
                "updateConditionalFormatRule": {
                    "index": 6,
                    "sheetId": 0,
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": checkbox_row_index - 1,
                                "endRowIndex": checkbox_row_index,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f"=AND($B{checkbox_row_index};NOT(AND(ARRAYFORMULA($I2:I{checkbox_row_index - 1}))))"}
                            },
                            "format": {
                                "backgroundColorStyle": {
                                    "rgbColor": {
                                        "red": 1,
                                        "green": 0,
                                        "blue": 0
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # Texto invisible que aparece si la casilla de Completado no es válida
            {
                "updateConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f"=AND($B{checkbox_row_index};NOT(AND(ARRAYFORMULA($I2:I{checkbox_row_index - 1}))))"}
                            },
                            "format": {
                                "textFormat": {
                                    "foregroundColorStyle": {
                                        "rgbColor": {
                                            "red": 0,
                                            "green": 0,
                                            "blue": 0
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "index": 7
                }
            }
        ]
    }

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=rev_id,
        body=body
    ).execute()

    packet['rev_id'] = rev_id

    return packet


def create_correction_sheet(creds, lang_code, title, packet):

    tra_id = packet['tra_id']
    rev_id = packet['rev_id']
    service = build("sheets", "v4", credentials=creds)

    # Get protected range id and lock first revision sheet
    protected_range_id = (
        service.spreadsheets().get(spreadsheetId=rev_id).execute()
    )
    protected_range_id = (
        protected_range_id
        ['sheets'][0]
        ['protectedRanges'][0]
        ["protectedRangeId"]
    )

    service.spreadsheets().batchUpdate(
        spreadsheetId=rev_id,
        body={
            "requests":
            [
                {
                    "updateProtectedRange": {
                        "protectedRange": {
                            "protectedRangeId": protected_range_id,
                            "unprotectedRanges": []
                        },
                        "fields": "unprotectedRanges"
                    }
                }
            ]
        }
    ).execute()

    # copy revision 1 results onto translation spreadsheet
    results = (
        service.spreadsheets().sheets().copyTo(
            spreadsheetId=rev_id,
            sheetId=0,
            body={"destinationSpreadsheetId": tra_id},
        ).execute()
    )

    copy_rev_id = results['sheetId']

    results = (
        service.spreadsheets().values().batchGet(
            spreadsheetId=rev_id,
            ranges=["A:I"],
        ).execute()
    )

    rows_to_correct = [
        (idx, row) for idx, row in enumerate(
            results['valueRanges'][0]['values']
        )
    ]
    rows_to_correct = [r for r in rows_to_correct if r[1][0].isnumeric()]
    rows_to_correct = [r for r in rows_to_correct if r[1][6] != 'Correcta']

    checkbox_row_index = [
        (idx, row) for idx, row in enumerate(
            results['valueRanges'][0]['values']
        ) if row[0] == 'Completado'
    ]
    checkbox_row_index = checkbox_row_index[0][0]

    rows_to_correct_validation_st = [
        f"ISBLANK($J{r[0] + 1})" for r in rows_to_correct
    ]
    rows_to_correct_validation_st = ";".join(rows_to_correct_validation_st)
    rows_to_correct_validation_st = f"OR({rows_to_correct_validation_st})"

    body = {
        "requests": [

            # Cambiar el título a la hoja de la segunda traducción
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": copy_rev_id,
                        "title": "Segunda traducción",
                    },
                    "fields": "title"
                },
            },

            # Crear línea divisoria entre primera y segunda traducciones
            {
                "repeatCell": {
                    "range": {
                        "sheetId": copy_rev_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 9,
                        "endColumnIndex": 10,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "borders": {
                                "left": {
                                    "style": "SOLID_THICK",
                                }
                            }
                        }
                    },
                    "fields": "userEnteredFormat.borders.left.style"
                },
            },

            # Ajustar grosor de la columna de segunda traducción
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": copy_rev_id,
                        "dimension": "COLUMNS",
                        "startIndex": 9,
                        "endIndex": 10,
                    },
                    "properties": {
                        "pixelSize": 300,
                    },
                    "fields": "pixelSize",
                }
            },

            # Protección para solo poder editar la segunda traducción
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "description": "Solo se permite la segunda traducción",
                        "range": {
                            "sheetId": copy_rev_id
                        },
                        "unprotectedRanges": [
                            {
                                "sheetId": copy_rev_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ] + [
                            {
                                "sheetId": copy_rev_id,
                                "startRowIndex": idx,
                                "endRowIndex": idx + 1,
                                "startColumnIndex": 9,
                                "endColumnIndex": 10,
                            } for idx in [row[0] for row in rows_to_correct]
                        ],
                        "editors": {
                            "users": [
                                "and_lou@gcloud.ua.es"
                            ]
                        }
                    },
                },
            },

            # Validar casilla de Completado: válida
            {
                "updateConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_rev_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{checkbox_row_index + 1};TRUE);NOT({rows_to_correct_validation_st}))'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0,
                                    "green": 1,
                                    "blue": 0
                                }
                            }
                        }
                    },
                    "index": 5
                }
            },

            # Validar casilla de Completado: no válida
            {
                "updateConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_rev_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{checkbox_row_index + 1};TRUE);{rows_to_correct_validation_st})'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1,
                                    "green": 0,
                                    "blue": 0
                                }
                            }
                        }
                    },
                    "index": 6
                }
            },

            # Texto invisible que aparece si la casilla de Completado no es válida
            {
                "updateConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_rev_id,
                                "startRowIndex": checkbox_row_index + 1,
                                "endRowIndex": checkbox_row_index + 2,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND(EQ($B{checkbox_row_index + 1};TRUE);{rows_to_correct_validation_st})'}
                            },
                            "format": {
                                "textFormat": {
                                    "foregroundColorStyle": {
                                        "rgbColor": {
                                            "red": 0,
                                            "green": 0,
                                            "blue": 0
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "index": 7
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=tra_id,
        body=body
    ).execute()

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "Segunda traducción!J1",
                "values": [["Segunda traducción"]],
            },
            {
                "range": "Segunda traducción!E1",
                "values": [["Primera traducción"]]
            },
            {
                "range": f"Segunda traducción!B{checkbox_row_index + 1}",
                "values": [[False]]
            }
        ]
    }
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=tra_id,
        body=body,
    ).execute()

    packet['stage'] = Stage.SECOND_TRANSLATION
    packet['last_stage_update'] = datetime.datetime.now().strftime(DATETIME_FORMAT)

    return packet


def create_revision_sheet(creds, lang_code, title, packet, r_max) -> (dict, int):

    rev_id = packet['rev_id']
    tra_id = packet['tra_id']

    service = build("sheets", "v4", credentials=creds)

    # Get protected range id and lock second translation sheet
    protected_range_id = (
        service.spreadsheets().get(spreadsheetId=tra_id).execute()
    )
    protected_range_id = (
        protected_range_id
        ['sheets'][1]
        ['protectedRanges'][0]
        ["protectedRangeId"]
    )

    service.spreadsheets().batchUpdate(
        spreadsheetId=tra_id,
        body={
            "requests":
            [
                {
                    "updateProtectedRange": {
                        "protectedRange": {
                            "protectedRangeId": protected_range_id,
                            "unprotectedRanges": []
                        },
                        "fields": "unprotectedRanges"
                    }
                }
            ]
        }
    ).execute()

    results = (
        service.spreadsheets().get(spreadsheetId=tra_id).execute()
    )

    copy_sheet_id = results["sheets"][1]["properties"]["sheetId"]

    results = (
        service.spreadsheets().sheets().copyTo(
            spreadsheetId=tra_id,
            sheetId=copy_sheet_id,
            body={"destinationSpreadsheetId": rev_id},
        ).execute()
    )

    copy_sheet_id = results["sheetId"]

    results = (
        service
        .spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=tra_id, ranges="Segunda traducción!A:Z"
        )
        .execute()
    )

    checkbox_row_index = [
        (idx, row) for idx, row in enumerate(
            results['valueRanges'][0]['values']
        ) if row[0] == 'Completado'
    ]
    checkbox_row_index = checkbox_row_index[0][0]

    rows_to_correct = [
        (idx, row) for idx, row in enumerate(
            results['valueRanges'][0]['values']
        )
    ]
    rows_to_correct = [r for r in rows_to_correct if r[1][0].isnumeric()]
    rows_to_correct = [r for r in rows_to_correct if r[1][6] != 'Correcta']
    rows_to_ignore = []

    if len(rows_to_correct) > r_max:
        rows_to_ignore = [
            row for row in rows_to_correct if row[1][6] == "Error menor"
        ]
        rows_to_correct = [
            row for row in rows_to_correct if row[1][6] != "Error menor"
        ]

        if len(rows_to_correct) > r_max:
            shuffle(rows_to_correct)
            rows_to_ignore += rows_to_correct[r_max:]
            rows_to_correct = rows_to_correct[:r_max]
        else:
            shuffle(rows_to_ignore)
            d = r_max - len(rows_to_correct)
            rows_to_correct += rows_to_ignore[:d]
            rows_to_ignore = rows_to_ignore[d:]

    rows_to_correct_validation_st = [f"$O{r[0] + 1}" for r in rows_to_correct]
    rows_to_correct_validation_st = ";".join(rows_to_correct_validation_st)
    rows_to_correct_validation_st = f"AND({rows_to_correct_validation_st})"

    body = {
        "requests": [

            # Cambiar el título de la hoja
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": copy_sheet_id,
                        "title": "2nda revisión",
                    },
                    "fields": "title"
                },
            },

            # Copiar y pegar validación de las columnas de «categoría», «severidad» y «comentario»
            {
                "copyPaste": {
                    "source": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 5,
                        "endColumnIndex": 8,
                    },
                    "destination": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 10,
                        "endColumnIndex": 13,
                    },
                    "pasteType": "PASTE_DATA_VALIDATION",
                    "pasteOrientation": "NORMAL",
                }
            },

            # Copiar encabezados de las columnas
            {
                "copyPaste": {
                    "source": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 5,
                        "endColumnIndex": 8,
                    },
                    "destination": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 10,
                        "endColumnIndex": 13,
                    },
                    "pasteType": "PASTE_NORMAL",
                    "pasteOrientation": "NORMAL",
                }
            },

            # Cambiar tamaño de celdas de «categoría» y «severidad»
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": copy_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 10,
                        "endIndex": 12,
                    },
                    "properties": {
                        "pixelSize": 100,
                    },
                    "fields": "pixelSize",
                }
            },

            # Cambiar de tamaño de celda de «comentario»
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": copy_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 12,
                        # "endIndex": 14,
                    },
                    "properties": {
                        "pixelSize": 300,
                    },
                    "fields": "pixelSize",
                }
            },

            # Ocultar la columna de validación
            {
                "updateDimensionProperties": {
                    "properties": {
                        "hiddenByUser": True,
                    },
                    "fields": "hiddenByUser",
                    "range": {
                        "sheetId": copy_sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 14,
                        "endIndex": 15,
                    }
                }
            },

            # Validación de cada fila
            {
                "repeatCell": {
                    "range": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": checkbox_row_index,
                        "startColumnIndex": 14,
                        "endColumnIndex": 15,
                    },
                    "cell": {
                        "userEnteredValue": {
                            "formulaValue": '=Y(NO(EQ($L2;""));O(Y(EQ($K2;"");EQ($M2;"");EQ($L2;"Correcta");EQ($N2;""));NO(O(EQ($K2;"");EQ($M2;"");EQ($L2;"Correcta");EQ($N2;"")))))',
                        },
                    },
                    "fields": "userEnteredValue"
                }
            },

            # casilla de validación: válida
            {
                "updateConditionalFormatRule": {
                    "index": 5,
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND($B{checkbox_row_index + 1};{rows_to_correct_validation_st})'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0,
                                    "green": 1,
                                    "blue": 0
                                }
                            }
                        }
                    },
                }
            },

            # casilla de validación: no válida
            {
                "updateConditionalFormatRule": {
                    "index": 6,
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND($B{checkbox_row_index + 1};NOT({rows_to_correct_validation_st}))'}
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1,
                                    "green": 0,
                                    "blue": 0
                                }
                            }
                        }
                    },
                }
            },

            # texto invisible
            {
                "updateConditionalFormatRule": {
                    "index": 7,
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": checkbox_row_index + 1,
                                "endRowIndex": checkbox_row_index + 2,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": f'=AND($B{checkbox_row_index + 1};NOT({rows_to_correct_validation_st}))'}
                            },
                            "format": {
                                "textFormat": {
                                    "foregroundColorStyle": {
                                        "rgbColor": {
                                            "red": 0,
                                            "green": 0,
                                            "blue": 0
                                        }
                                    }
                                }
                            }
                        }
                    },
                }
            },

            # Resaltar casilla de «severidad» si se marca como correcta pero hay categorías de errror o comentario
            {
                "addConditionalFormatRule": {
                    "index": 8,
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                                "startColumnIndex": 11,
                                "endColumnIndex": 12,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=AND(EQ($L2;"Correcta");NOT(AND(EQ($K2;"");EQ($M2;"");EQ($N2;""))))'}
                            },
                            "format": {
                                "backgroundColor": COLOR_CRITICAL
                            }
                        }
                    },
                }
            },

            {
                "addConditionalFormatRule": {
                    "index": 8,
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": 1000,
                            },
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "CUSTOM_FORMULA",
                                "values": {"userEnteredValue": '=OR(NOT(OR(EQ($L2;"Correcta");EQ($K2;"");EQ($M2;"");EQ($N2;"")));AND(EQ($L2;"Correcta");EQ($K2;"");EQ($M2;"");EQ($N2;"")))'}
                            },
                            "format": {
                                "backgroundColor": COLOR_GOOD
                            }
                        }
                    },
                }
            },

            # Protección para solo poder editar la segunda revisión
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": copy_sheet_id,
                        },
                        "description": "Revisiones no permitidas",
                        "unprotectedRanges": [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": idx,
                                "endRowIndex": idx + 1,
                                "startColumnIndex": 10,
                                "endColumnIndex": 14,
                            } for idx in [row[0] for row in rows_to_correct]
                        ] + [
                            {
                                "sheetId": copy_sheet_id,
                                "startRowIndex": checkbox_row_index,
                                "endRowIndex": checkbox_row_index + 1,
                                "startColumnIndex": 1,
                                "endColumnIndex": 2,
                            }
                        ],
                        "editors": {
                            "users": [
                                "and_lou@gcloud.ua.es",
                            ]
                        }
                    }
                }
            },
        ] + [

            # Resaltar filas que no deben ser corregidas por segunda vez
            {
                "repeatCell": {
                    "range": {
                        "sheetId": copy_sheet_id,
                        "startRowIndex": idx,
                        "endRowIndex": idx + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColorStyle": {
                                "rgbColor": COLOR_IGNORE
                            },
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColorStyle"
                }
            } for idx in [row[0] for row in rows_to_ignore]
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=rev_id,
        body=body
    ).execute()

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "2nda revisión!N1:O1",
                "values": [["Traducción final", "Fila válida"]],
            },
            {
                "range": f"2nda revisión!B{checkbox_row_index + 1}",
                "values": [[False]]
            }
        ]
    }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=rev_id,
        body=body,
    ).execute()

    packet['stage'] = Stage.SECOND_REVISION
    packet['last_stage_update'] = datetime.datetime.now().strftime(DATETIME_FORMAT)

    return packet, len(rows_to_correct)


def create_vocab_spreadsheet(creds, lang, permission_emails):
    # Create vocab spreadsheet file
    body = {
        "properties": {
            "title": f"vocabulario_{lang}"
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": "vocabulario"
                }
            }
        ]
    }

    service = build("sheets", "v4", credentials=creds)
    results = (
        service.spreadsheets().create(
            body=body,
            fields="spreadsheetId"
        ).execute()
    )
    vocab_id = results.get("spreadsheetId")

    # Check if lang vocab file exists and create one if not
    if not os.path.isfile(f"../data/{lang}/vocab.json"):
        vocab = VOCAB_FLORES_PLUS
        if not os.path.isdir(f"../data/{lang}"):
            os.makedirs(f"../data/{lang}")
        with open(f"../data/{lang}/vocab.json", "w") as f:
            f.write(json.dumps(VOCAB_FLORES_PLUS, indent=2, ensure_ascii=False))
    else:
        with open(f"../data/{lang}/vocab.json") as f:
            vocab = json.loads(f.read())

    # Put data in
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": "A1:D1",
                "values": [
                    [
                        "Frecuencia",
                        "Término",
                        "Traducción",
                        "Nota"
                    ]
                ],
            },
            {
                "range": "A2:D",
                "values": [
                    [vocab[key]['freq'], key, vocab[key]['def'], vocab[key]['notes']] for key, value in vocab.items()
                ]
            }
        ]
    }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=vocab_id,
        body=body
    ).execute()

    # Format the data
    body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.bold"
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "startRowIndex": 1,
                        "endRowIndex": 1000
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "wrapStrategy": "WRAP"
                        }
                    },
                    "fields": "userEnteredFormat.wrapStrategy",
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": len(vocab.keys())
                    },
                    "properties": {
                        "pixelSize": 300,
                    },
                    "fields": "pixelSize",
                }
            },
            {
                "insertDimension": {
                    "range": {
                        "dimension": "ROWS",
                        "startIndex": len(vocab.keys()) + 1,
                        "endIndex": len(vocab.keys()) + 100
                    },
                    "inheritFromBefore": True
                }
            },
            {
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": 0,
                        },
                        "description": "Vocabulario",
                        "unprotectedRanges": [
                            {
                                "sheetId": 0,
                                "startRowIndex": 1,
                                "endRowIndex": len(vocab.keys()) + 100,
                                "startColumnIndex": 2,
                                "endColumnIndex": 4,
                            },
                            {
                                "sheetId": 0,
                                "startRowIndex": len(vocab.keys()) + 1,
                                "endRowIndex": len(vocab.keys()) + 100,
                                "startColumnIndex": 1,
                                "endColumnIndex": 4,
                            },
                        ],
                        "editors": {
                            "users": [
                                "and_lou@gcloud.ua.es",
                            ]
                        }
                    }
                }
            },
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=vocab_id,
        body=body
    ).execute()

    # Move vocabulary spreadsheet into corresponding folder
    service = build("drive", "v3", credentials=creds)
    query = f"mimeType = 'application/vnd.google-apps.folder' and '{FOLDER_ID_TAREA_DE_TRADUCCION}' in parents and name = '{lang}'"
    results = service.files().list(q=query).execute()
    parent_folder = results['files'][0]['id']

    file = service.files().get(
        fileId=vocab_id, fields="parents"
    ).execute()
    previous_parents = ",".join(file.get("parents"))
    file = (
        service.files()
        .update(
            fileId=vocab_id,
            addParents=parent_folder,
            removeParents=previous_parents,
            fields="id, parents",
        )
    ).execute()

    # Create permissions for translators and revisor
    for email in permission_emails:
        body = {
            "type": "user",
            "role": "writer",
            "emailAddress": email
        }

        service.permissions().create(fileId=vocab_id, body=body).execute()

    return vocab_id
