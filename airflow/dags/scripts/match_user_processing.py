import pandas as pd
import numpy as np

import os
import json
import time
import requests
import datetime 
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

import warnings
warnings.filterwarnings("ignore")

from sqlalchemy import create_engine, text

from scripts.sub_function import fetch_data, append_match_user_data



def match_user_processing(_api_key, _file_dir, _dag_exec_time) :
    start_time = time.time()

    if not os.path.exists(_file_dir):
        os.makedirs(_file_dir)

    headers = {'x-nxopen-api-key': _api_key}

    matchType_df = pd.read_csv(os.path.join(_file_dir, 'metadata/matchType_metadata.csv'))

    match_id_url = 'https://open.api.nexon.com/fconline/v1/match?'
    match_id_params = {'matchtype' : matchType_df.loc[matchType_df['matchName'] == '공식경기', 'matchType'].iloc[0], 
                       'offset' : 0, 'limit' : 81}

    match_id_json = fetch_data(match_id_url, match_id_params, headers) 
    
    match_user_data = []
    new_user_dict = {}

    for match_ouid in match_id_json : 
        match_detail_url = 'https://open.api.nexon.com/fconline/v1/match-detail?'
        match_detail_params = {'matchid' : match_ouid}

        match_detail = fetch_data(match_detail_url, match_detail_params, headers)

        if not match_detail : 
            continue 

        for match_user in match_detail['matchInfo'] : 
            append_match_user_data(match_user_data, match_ouid, match_user, new_user_dict)

    match_user_df = pd.DataFrame(match_user_data)
    print('All request from match :', len(match_user_df))

    filtered_match_user_df = match_user_df.dropna()
    filtered_match_user_df.to_csv(os.path.join(_file_dir, f'match_user_{_dag_exec_time}.csv'), index = False)
    print('Filtered request from match :', len(filtered_match_user_df))

    new_user_dict = filtered_match_user_df.groupby('user_ouid')['user_nickname'].first().to_dict()

    # Save the dictionary to a JSON file
    with open(os.path.join(_file_dir, 'new_user_dict.json'), 'w') as json_file:
        json.dump(new_user_dict, json_file, ensure_ascii = False, indent = 4)

    print('New user from match :', len(new_user_dict))

    end_time = time.time()

    print(f"Time elapsed: {end_time - start_time:.2f} seconds For match_user_processing")