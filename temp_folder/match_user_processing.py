import pandas as pd
import numpy as np

import time
import requests
import datetime 
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

import warnings
warnings.filterwarnings("ignore")

import sys 
sys.path.append('C:/Users/dohyu/Desktop/Github/side_proj_fifa')

from sqlalchemy import create_engine, text
from sub_function import fetch_data, db_conn, position_rating, append_match_user_data
from queries import (CREATE_MATCH_USER_TABLE_QUERY, INSERT_MATCH_USER_TABLE_QUERY, 
                     CREATE_USER_METADATA_TABLE_QUERY, INSERT_USER_METADATA_TABLE_QUERY)



start_time = time.time()

api_key = 'test_b375f597f54e36891fce7c2f065cd1a9e2d8c3c1bbbe3330e29246630a7c0345efe8d04e6d233bd35cf2fabdeb93fb0d'
headers = {'x-nxopen-api-key': api_key}

matchType_df = pd.read_csv('./metadata/matchType_metadata.csv')

match_id_url = 'https://open.api.nexon.com/fconline/v1/match?'
match_id_params = {'matchtype' : matchType_df.loc[matchType_df['matchName'] == '공식경기', 'matchType'].iloc[0], 
                   'offset' : 0, 
                   'limit' : 81}

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
print('Filtered request from match :', len(filtered_match_user_df))

new_user_dict = filtered_match_user_df.groupby('user_ouid')['user_nickname'].first().to_dict()

engine = db_conn('root', 'Dhyoon96!', '127.0.0.1', 'side_proj_fco')

create_user_metadata_table_query = CREATE_USER_METADATA_TABLE_QUERY
insert_user_metadata_table_query = INSERT_USER_METADATA_TABLE_QUERY
create_match_user_table_query = CREATE_MATCH_USER_TABLE_QUERY
insert_match_user_table_query = INSERT_MATCH_USER_TABLE_QUERY

with engine.connect() as connection:
    trans = connection.begin()  
    
    try:
        connection.execute(text(create_match_user_table_query))
        connection.execute(text(create_user_metadata_table_query))

        try:
            count_user = 0
            for new_user_ouid, new_user_nickname in new_user_dict.items():
                connection.execute(
                    text(insert_user_metadata_table_query),
                    {'user_ouid': new_user_ouid, 'user_nickname': new_user_nickname})
                count_user += 1

            count_match = 0
            for index, row in filtered_match_user_df.iterrows():
                connection.execute(text(insert_match_user_table_query), row.to_dict())
                count_match += 1

            print(f'Successfully added {count_user} user and {count_match} match data to tables')

        except Exception as insert_e:
            print(f"Error occurred while adding data: {insert_e}")
            trans.rollback()
            raise

        trans.commit()

    except Exception as create_e:
        print(f"Error occurred while creating tables: {create_e}")
        trans.rollback()

engine.dispose()

end_time = time.time()

print(f"Time elapsed: {end_time - start_time:.2f} seconds")
