import numpy as np

import requests

import sqlalchemy

from sqlalchemy import create_engine, text



def fetch_data(url_, params_, headers_):
    response = requests.get(url_, params = params_, headers = headers_)

    if response.status_code == 200:
        # print(f"Successed to fetch data from {url_}.") 
        return response.json()
        
    else:
        print(f"Error: Failed to fetch data from {url_}. Status Code: {response.status_code}")
        return None

def db_conn(username_, password_, host_, port_, database_) : 
    db_engine = sqlalchemy.engine.URL.create(
        drivername = "mysql+pymysql",
        username = username_,
        password = password_,
        host = host_,
        port = port_,
        database = database_,
    )

    return create_engine(db_engine)

def position_rating(match_user_) :  
    attack_position = [i for i in range(9, 20)]
    middle_position = [i for i in range(20, 28)]
    defense_position = [i for i in range(1, 9)]
    goalkeeper_position = [0]
    
    attack_rating = []
    middle_rating = []
    defense_rating = []
    goalkeeper_rating = []
    
    for player in match_user_['player'] : 
        if player['spPosition'] == 28 :                             # 후보선수 제외
            continue

        elif player['spPosition'] in attack_position :              # 공격 평점
            attack_rating.append(player['status']['spRating'])

        elif player['spPosition'] in middle_position :              # 미들 평점
            middle_rating.append(player['status']['spRating'])

        elif player['spPosition'] in defense_position :             # 수비 평점
            defense_rating.append(player['status']['spRating'])

        else :                                                      # 골키퍼 평점 
            goalkeeper_rating.append(player['status']['spRating'])

    return round(np.mean(attack_rating), 2), round(np.mean(middle_rating), 2), round(np.mean(defense_rating), 2), round(np.mean(goalkeeper_rating), 2)

def append_match_user_data(match_user_data_, match_ouid_, match_user_, new_user_dict_):
    attack_position_ratings, middle_position_ratings, defense_position_ratings, goalkeeper_position_ratings = position_rating(match_user_)
        
    match_user_data_.append({
        'match_id': match_ouid_,
        'user_ouid': match_user_['ouid'],
        'user_nickname': match_user_['nickname'],
        'match_result': match_user_['matchDetail']['matchResult'],
        'match_possession': match_user_['matchDetail']['possession'],
        'match_avg_rating': match_user_['matchDetail']['averageRating'],
        'match_total_dribble': match_user_['matchDetail']['dribble'],
        'match_total_pass_try': match_user_['pass']['passTry'],
        'match_total_pass_suc': match_user_['pass']['passSuccess'],
        'match_total_shoot': match_user_['shoot']['shootTotal'],
        'match_total_shoot_eff': match_user_['shoot']['effectiveShootTotal'],
        'match_total_goal': match_user_['shoot']['goalTotal'],
        'attack_position_ratings': attack_position_ratings,
        'middle_position_ratings': middle_position_ratings,
        'defense_position_ratings': defense_position_ratings,
        'goalkeeper_position_ratings': goalkeeper_position_ratings,

        'match_total_pass_short_try': match_user_['pass']['shortPassTry'],
        'match_total_pass_short_suc': match_user_['pass']['shortPassSuccess'],
        'match_total_pass_long_try': match_user_['pass']['longPassTry'],
        'match_total_pass_long_suc': match_user_['pass']['longPassSuccess'],
        'match_total_pass_through_try': match_user_['pass']['throughPassTry'],
        'match_total_pass_through_suc': match_user_['pass']['throughPassSuccess'],
        'match_total_shoot_outpenalty_try': match_user_['shoot']['shootOutPenalty'],
        'match_total_shoot_outpenalty_suc': match_user_['shoot']['goalOutPenalty'],
        'match_total_shoot_inpenalty_try': match_user_['shoot']['shootInPenalty'],
        'match_total_shoot_inpenalty_suc': match_user_['shoot']['goalInPenalty']})
