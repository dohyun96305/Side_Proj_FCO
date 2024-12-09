import pandas as pd
import numpy as np

import os
import json
import time
import datetime 
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

import warnings
warnings.filterwarnings("ignore")

from sqlalchemy import create_engine, text

from scripts.sub_function import db_conn
from scripts.queries import (CREATE_MATCH_USER_TABLE_QUERY, INSERT_MATCH_USER_TABLE_QUERY, 
                     CREATE_USER_METADATA_TABLE_QUERY, INSERT_USER_METADATA_TABLE_QUERY)



def match_user_to_sql(_file_dir, _task_time, _user_name, _password, _host, _port, _database) :
    start_time = time.time()

    with open(os.path.join(_file_dir, 'new_user_dict.json'), 'r') as file:
        new_user_dict = json.load(file)

    filtered_match_user_df = pd.read_csv(os.path.join(_file_dir, f'match_user_{_task_time}.csv'))
    
    engine = db_conn(_user_name, _password, _host, _port, _database)

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

    print(f"Time elapsed: {end_time - start_time:.2f} seconds For match_user_to_sql")