import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT 
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL, Identifier

'''
CREATE ROLE [role_name] WITH LOGIN CREATEDB PASSWORD '[password]';
sudo -i -u postgres
CREATE database witcher_trpg_db

comands for create Database in postgres for this bot:
    

'''

DB_HOST = "localhost"
DB_NAME = "witcher_trpg_db"
DB_USER = "bot"
DB_PASS = "bot"

TABLE_users ="""
CREATE TABLE users ( 
    id BIGINT PRIMARY KEY, 
    first_name varchar(80), 
    last_name varchar(80), 
    username varchar(80), 
    language_code varchar(80), 
    first_start DATE
    );"""

TABLE_attack_session = """
CREATE TABLE attack_session(
    id serial PRIMARY KEY,
    user_id BIGINT references users(id),
    session_date DATE,
    have_own_weapon varchar(80),
    type_of_attack varchar(80),
    weapon varchar(80),
    fast_or_hard varchar(80),
    weapon_accuracy varchar(80),
    place_penalty varchar(80),
    distance varchar(80),
    mod INT,
    is_attack_more varchar(80),
    body varchar(80),
    weapon_damage INT,
    enemy_type varchar(80),
    place_humanoid varchar(80),
    place_monster varchar(80),
    is_damage_more varchar(80),
    damage_hit INT,
    resistance_or varchar(80),
    damage_hurt varchar(80),
    critical_injury varchar(80)
    );"""
    
TABLE_multiple_modifier = """
CREATE TABLE mod ( 
    id serial PRIMARY KEY, 
    session_id INT references attack_session(id),
    value varchar(80)
    );"""


TABLE_critical_injury = """
CREATE TABLE critical_injury ( 
    attack_more_defense varchar(80),
    critical_level varchar(80),
    additional_damage INT,
    critical_injury_roll varchar(80),
    critical_effect_name varchar(80),
    critical_effect text,
    critical_stabilization text,
    critical_healing text
    );"""

TABLE_defense_session ="""
CREATE TABLE defense_session(
    id serial PRIMARY KEY,
    user_id BIGINT references users(id),
    session_date DATE,
    first_defense varchar(80),
    lose_stamina varchar(20),
    type_of_attack varchar(80),
    attack_weapon varchar(80),
    hold_shield varchar(80),
    type_of_defense varchar(80),
    defense_weapon varchar(80),
    opponents varchar(80),
    d_mod INT,
    d_effects INT,
    is_attack_more varchar(80),
    place varchar(80),
    armor INT,
    damage_hit INT,
    damage_pierced INT,
    resistance_or varchar(80),
    damage_hurt varchar(80),
    critical_injury varchar(80)
    );"""    
    
TABLE_multiple_d_modifier = """
CREATE TABLE d_mod ( 
    id serial PRIMARY KEY, 
    session_id INT references defense_session(id),
    value varchar(80)
    );"""

with psycopg2.connect(
    host = DB_HOST,
    database = DB_NAME,
    user = DB_USER,
    password = DB_PASS,
    ) as conn:
    
    with conn.cursor(cursor_factory=DictCursor) as cur:
                        
        # cur.execute(SQL(TABLE_users))
        cur.execute(SQL(TABLE_attack_session))
        cur.execute(SQL(TABLE_multiple_modifier))
        
        cur.execute(SQL(TABLE_defense_session))
        cur.execute(SQL(TABLE_multiple_d_modifier))

