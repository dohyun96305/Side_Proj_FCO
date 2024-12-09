import pandas as pd

import os
import requests
import warnings
warnings.filterwarnings("ignore")

from scripts.sub_function import fetch_data



def get_metadata(_api_key, _file_dir): 

    if not os.path.exists(os.path.join(_file_dir, 'metadata')):
        os.makedirs(os.path.join(_file_dir, 'metadata'))

    headers = {'x-nxopen-api-key': _api_key}

    match_url = 'https://open.api.nexon.com/static/fconline/meta/matchtype.json'
    division_url = 'https://open.api.nexon.com/static/fconline/meta/division.json'

    match_json = fetch_data(match_url, None, headers)
    division_json = fetch_data(division_url, None, headers)

    if match_json:
        match_df = pd.DataFrame(match_json)
        match_df = match_df.rename(columns = {'matchtype' : 'matchType', 'desc' : 'matchName'})
        match_df.to_csv(os.path.join(_file_dir, 'metadata', 'matchType_metadata.csv'), index = False)

    if division_json:
        division_df = pd.DataFrame(division_json)
        division_df = division_df.rename(columns  = {'divisionId': 'division'})
        division_df.to_csv(os.path.join(_file_dir, 'metadata', 'division_metadata.csv'), index = False)