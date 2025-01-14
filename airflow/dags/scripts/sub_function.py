import numpy as np

import requests

import sqlalchemy

from sqlalchemy import create_engine, text



def fetch_data(_url, _params, _headers):
    response = requests.get(_url, params = _params, headers = _headers)

    if response.status_code == 200:
        # print(f"Successed to fetch data from {url_}.") 
        return response.json()
        
    else:
        print(f"Error: Failed to fetch data from {_url}. Status Code: {response.status_code}")

        return None

def db_conn(_username, _password, _host, _port, _database) : 
    db_engine = sqlalchemy.engine.URL.create(
        drivername = "mysql+pymysql",
        username = _username,
        password = _password,
        host = _host,
        port = _port,
        database = _database,
    )

    return create_engine(db_engine)

def position_rating(_match_user) :  
    attack_position = [i for i in range(9, 20)]
    middle_position = [i for i in range(20, 28)]
    defense_position = [i for i in range(1, 9)]
    goalkeeper_position = [0]
    
    attack_rating = []
    middle_rating = []
    defense_rating = []
    goalkeeper_rating = []
    
    for player in _match_user['player'] : 
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

def shoot_time_convert(_shoot_time) :
    half_time_interval = 2**24

    if 0 <= _shoot_time < half_time_interval - 1 :  # 전반전
        converted_time = _shoot_time
        
    elif half_time_interval <= _shoot_time < 2 * half_time_interval - 1:    # 후반전
        converted_time = _shoot_time - half_time_interval + 45 * 60
        
    elif 2 * half_time_interval <= _shoot_time < 3 * half_time_interval - 1:    # 연장-전반
        converted_time = _shoot_time - 2 * half_time_interval + 90 * 60
        
    elif 3 * half_time_interval <= _shoot_time < 4 * half_time_interval - 1:    # 연장-후반
        converted_time = _shoot_time - 3 * half_time_interval + 105 * 60
        
    elif 4 * half_time_interval <= _shoot_time < 5 * half_time_interval - 1:    # 승부차기
        converted_time = _shoot_time - 4 * half_time_interval + 120 * 60

    return converted_time 

def append_match_user_data(_match_user_data, _match_ouid, _match_user):
    attack_position_ratings, middle_position_ratings, defense_position_ratings, goalkeeper_position_ratings = position_rating(_match_user)
    
    _match_user_data.append({
        'match_id': _match_ouid,
        'user_ouid': _match_user['ouid'],
        'user_nickname': _match_user['nickname'],
        'match_result': _match_user['matchDetail']['matchResult'],
        'match_endtype': _match_user['matchDetail']['matchEndType'],
        'match_possession': _match_user['matchDetail']['possession'],
        'match_avg_rating': _match_user['matchDetail']['averageRating'],
        'match_total_dribble': _match_user['matchDetail']['dribble'],
        'match_total_pass_try': _match_user['pass']['passTry'],
        'match_total_pass_suc': _match_user['pass']['passSuccess'],
        'match_total_shoot': _match_user['shoot']['shootTotal'],
        'match_total_shoot_eff': _match_user['shoot']['effectiveShootTotal'],
        'match_total_goal': _match_user['shoot']['goalTotal'],
        'attack_position_ratings': attack_position_ratings,
        'middle_position_ratings': middle_position_ratings,
        'defense_position_ratings': defense_position_ratings,
        'goalkeeper_position_ratings': goalkeeper_position_ratings,

        'match_total_pass_short_try': _match_user['pass']['shortPassTry'],
        'match_total_pass_short_suc': _match_user['pass']['shortPassSuccess'],
        'match_total_pass_long_try': _match_user['pass']['longPassTry'],
        'match_total_pass_long_suc': _match_user['pass']['longPassSuccess'],
        'match_total_pass_through_try': _match_user['pass']['throughPassTry'],
        'match_total_pass_through_suc': _match_user['pass']['throughPassSuccess'],
        'match_total_shoot_outpenalty_try': _match_user['shoot']['shootOutPenalty'],
        'match_total_shoot_outpenalty_suc': _match_user['shoot']['goalOutPenalty'],
        'match_total_shoot_inpenalty_try': _match_user['shoot']['shootInPenalty'],
        'match_total_shoot_inpenalty_suc': _match_user['shoot']['goalInPenalty']})

def append_shoot_detail_data(_shoot_detail_data, _match_ouid, _match_user_ouid, match_result, _shoot_detail):
    _shoot_detail_data.append({
        'match_id': _match_ouid,
        'user_ouid': _match_user_ouid,
        'match_result': match_result,
        'shoot_result': _shoot_detail['result'],
        'shoot_time': shoot_time_convert(_shoot_detail['goalTime']),
        'shoot_position_x': _shoot_detail['x'],
        'shoot_position_y': _shoot_detail['y'],
        'shoot_assist': _shoot_detail['assist'],
        'shoot_assist_X': _shoot_detail['assistX'],
        'shoot_assist_Y': _shoot_detail['assistY'],
        'shoot_inpenalty': _shoot_detail['inPenalty']
    })
