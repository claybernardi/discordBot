import os

import requests
import json

OUTFILE_NAME = 'cards/default_cards.json'
CARDS_FOLDER = 'cards'

def make_default_cards_json():
    os.makedirs(CARDS_FOLDER, exist_ok=True)

    # Call the scryfall bulk data api, and retrieve the download link to default_cards and store it in SCRYFALL_URL
    r = requests.get('https://api.scryfall.com/bulk-data')
    bulk_data_json = r.json()

    SCRYFALL_URL = bulk_data_json['data'][2]['download_uri']

    # Download default cards and save it to default_cards.json
    data = requests.get(SCRYFALL_URL)

    print(f'Converting from type: {type(data)} to json')
    data = data.json()
    print(f'Coverted to: {type(data)}')

    # NOTE REMOVE INDENT WHEN DONE, IT WILL RUN FASTER
    with open(OUTFILE_NAME, 'w') as outfile:
        json.dump(data, outfile)

    print(f'File written to {OUTFILE_NAME}')