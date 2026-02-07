import json
from sheets_create import update_report_spreadsheet
from util import authenticate

creds = authenticate()
with open("../data/state.json") as f:
    state = json.loads(f.read())

for lang in state.keys():
    update_report_spreadsheet(creds, state, lang)
