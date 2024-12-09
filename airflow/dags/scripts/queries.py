CREATE_MATCH_USER_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS match_user (
        match_id VARCHAR(40),         
        user_ouid VARCHAR(40),        
        user_nickname VARCHAR(50),      
        match_result VARCHAR(5),                             
        match_possession INT,                               
        match_avg_rating FLOAT,                              
        match_total_dribble INT,                              
        match_total_pass_try INT,                             
        match_total_pass_suc INT,                             
        match_total_shoot INT,                                 
        match_total_shoot_eff INT,                            
        match_total_goal INT,         
        attack_position_ratings FLOAT,
        middle_position_ratings FLOAT,
        defense_position_ratings FLOAT,
        goalkeeper_position_ratings FLOAT,                       
        match_total_pass_short_try INT,
        match_total_pass_short_suc INT,
        match_total_pass_long_try INT,
        match_total_pass_long_suc INT,
        match_total_pass_through_try INT,
        match_total_pass_through_suc INT,
        match_total_shoot_outpenalty_try INT,
        match_total_shoot_outpenalty_suc INT,
        match_total_shoot_inpenalty_try INT,
        match_total_shoot_inpenalty_suc INT, 
        
        PRIMARY KEY (match_id, user_ouid)
    );   
"""

INSERT_MATCH_USER_TABLE_QUERY = """
    INSERT IGNORE INTO match_user (match_id, user_ouid, user_nickname, match_result, match_possession, match_avg_rating, 
                                   match_total_dribble, match_total_pass_try, match_total_pass_suc, match_total_shoot, 
                                   match_total_shoot_eff, match_total_goal, 
                                   attack_position_ratings, middle_position_ratings, defense_position_ratings, goalkeeper_position_ratings,
                                   match_total_pass_short_try, match_total_pass_short_suc, 
                                   match_total_pass_long_try, match_total_pass_long_suc, 
                                   match_total_pass_through_try, match_total_pass_through_suc, 
                                   match_total_shoot_outpenalty_try, match_total_shoot_outpenalty_suc, 
                                   match_total_shoot_inpenalty_try, match_total_shoot_inpenalty_suc)
    VALUES (:match_id, :user_ouid, :user_nickname, :match_result, :match_possession, :match_avg_rating, 
            :match_total_dribble, :match_total_pass_try, :match_total_pass_suc, :match_total_shoot, 
            :match_total_shoot_eff, :match_total_goal,
            :attack_position_ratings, :middle_position_ratings, :defense_position_ratings, :goalkeeper_position_ratings,
            :match_total_pass_short_try, :match_total_pass_short_suc, 
            :match_total_pass_long_try, :match_total_pass_long_suc, 
            :match_total_pass_through_try, :match_total_pass_through_suc, 
            :match_total_shoot_outpenalty_try, :match_total_shoot_outpenalty_suc, 
            :match_total_shoot_inpenalty_try, :match_total_shoot_inpenalty_suc);
"""

CREATE_USER_METADATA_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS user_metadata (
        user_ouid VARCHAR(40) PRIMARY KEY,
        user_nickname VARCHAR(50) NOT NULL);
"""

INSERT_USER_METADATA_TABLE_QUERY = """
    INSERT IGNORE INTO user_metadata (user_ouid, user_nickname)
    VALUES (:user_ouid, :user_nickname);    
"""