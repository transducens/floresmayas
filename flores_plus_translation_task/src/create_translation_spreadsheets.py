from sheets_create import *
from constants import DEVTEST
from util import authenticate
from tqdm import tqdm

creds = authenticate()
# sents = DEVTEST[3]
lang_code = "dum"
title = 'test_using_update_2'
tra_email = "feasinde@gmail.com"
rev_email = "lourios.andres@gmail.com"

for i in tqdm(range(2,3)):
    create_translation_spreadsheet(
        creds, DEVTEST[i], "dum", f"test_{i}", "feasinde@gmail.com", "lourios.andres@gmail.com"
    )
