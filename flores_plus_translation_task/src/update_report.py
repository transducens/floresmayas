import json
from sheets_create import update_report_spreadsheet
from util import authenticate

with open("../data/config.json") as f:
    if not json.loads(f.read())['start_translation']:
        exit(0)

creds = authenticate()
with open("../data/state.json") as f:
    state = json.loads(f.read())

from icecream import ic
for lang in state.keys():
    ic(lang)
    update_report_spreadsheet(creds, state, lang)
