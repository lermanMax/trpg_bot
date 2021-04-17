import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL, Identifier

import datetime 

class DB_module:
    
    def __init__(self, DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT):
        self.DB_dict = {'host': DB_HOST,
                        'database': DB_NAME,
                        'user': DB_USER,
                        'password': DB_PASS,
                        'port': DB_PORT}
        
        
    """users"""    
    def add_user(self, user_id, first_name, last_name, username, language_code):
        if self.get_user(user_id): return 'user exist'
        
        first_start = datetime.date.today()
        
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
    
        insert_into_users="""insert into users
                          (id, first_name, last_name, 
                           username, language_code, first_start) 
                          values (%s, %s, %s, %s, %s, %s);"""
        values = (user_id, first_name, last_name, 
                  username, language_code, first_start)
                
        cur.execute(insert_into_users, values)
        conn.commit()
        cur.close()
        conn.close()
        return 'user added'
    
    
    def get_user(self, user_id):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
                
        select_users = "select * from users where id = %s;"
        data = (user_id,)
        
        cur.execute(select_users, data)
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return result
    
    
    """attack_session"""
    def new_attack_session(self, user_id):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        session_date = datetime.date.today()
        insert_into_attack_session="""insert into attack_session
                                      (user_id, session_date) 
                                      values (%s, %s)
                                      RETURNING id;"""
        values = (user_id, session_date)
        cur.execute(insert_into_attack_session, values)
        session_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        return session_id
    
    
    def get_attack_session(self, session_id):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        select_attack_session = "select * from attack_session where id = %s;"
        data = (session_id,)
    
        cur.execute(select_attack_session, data)
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return result
    
    
    def save_attack(self, session_id, question_name, answer):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        cur.execute(SQL("""
                            UPDATE attack_session 
                            SET {} = %(answer)s
                            WHERE id = %(id)s
                            ;
                            """).format(Identifier(question_name)), 
                            {
                            'id': session_id,
                            'answer': answer
                            })
        
        # update_attack_session= """UPDATE attack_session 
        #                           SET %s = %s
        #                           WHERE id = %s ;"""
        # values = (answer, session_id)
        # cur.execute(update_attack_session, values)
        
        conn.commit()
        cur.close()
        conn.close()
        return 'saved'
    
    
    def save_attack_multiple_answer(self, session_id, name, answer):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        cur.execute(SQL(""" select * from {}
                            where 
                            session_id = %(session_id)s 
                            and value = %(value)s ;
                            """).format(Identifier(name)), 
                            {'session_id': session_id,
                             'value': answer})
        result = cur.fetchall()
        
        if not result: 
            cur.execute(SQL(""" insert into {}
                                (session_id, value) 
                                values (%(session_id)s, %(value)s)
                                ;
                                """).format(Identifier(name)), 
                                {
                                'session_id': session_id,
                                'value': answer
                                })
        else:
            cur.execute(SQL(""" delete from {}
                                where 
                                session_id = %(session_id)s 
                                and value = %(value)s ;
                                """).format(Identifier(name)), 
                                {'session_id': session_id,
                                 'value': answer})
            
        conn.commit()
        cur.close()
        conn.close()
        return 'saved'
    
    
    def get_selected_options_from_attack(self, session_id, name):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        # select_attack_session = "select * from attack_session where id = %s;"
        # data = (session_id,)
        # cur.execute(select_attack_session, data)
        
        cur.execute(SQL(""" select * from {}
                            where session_id = %(session_id)s;
                            """).format(Identifier(name)), 
                            {'session_id': session_id })
        result = cur.fetchall()
        
        conn.commit()
        cur.close()
        conn.close()
        return result
    
    
    """defense_session"""
    def new_defense_session(self, user_id):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        session_date = datetime.date.today()
        insert_into_defense_session="""insert into defense_session
                                      (user_id, session_date) 
                                      values (%s, %s)
                                      RETURNING id;"""
        values = (user_id, session_date)
        cur.execute(insert_into_defense_session, values)
        session_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        return session_id
    
    
    def get_defense_session(self, session_id):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        select_defense_session="select * from defense_session where id = %s;"
        data = (session_id,)
    
        cur.execute(select_defense_session, data)
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return result
    
    
    def save_defense(self, session_id, question_name, answer):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        cur.execute(SQL("""
                            UPDATE defense_session 
                            SET {} = %(answer)s
                            WHERE id = %(id)s
                            ;
                            """).format(Identifier(question_name)), 
                            {
                            'id': session_id,
                            'answer': answer
                            })
        
        conn.commit()
        cur.close()
        conn.close()
        return 'saved'
    
    
    def save_defense_multiple_answer(self, session_id, name, answer):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        cur.execute(SQL(""" select * from {}
                            where 
                            session_id = %(session_id)s 
                            and value = %(value)s ;
                            """).format(Identifier(name)), 
                            {'session_id': session_id,
                             'value': answer})
        result = cur.fetchall()
        
        if not result: 
            cur.execute(SQL(""" insert into {}
                                (session_id, value) 
                                values (%(session_id)s, %(value)s)
                                ;
                                """).format(Identifier(name)), 
                                {
                                'session_id': session_id,
                                'value': answer
                                })
        else:
            cur.execute(SQL(""" delete from {}
                                where 
                                session_id = %(session_id)s 
                                and value = %(value)s ;
                                """).format(Identifier(name)), 
                                {'session_id': session_id,
                                 'value': answer})
            
        conn.commit()
        cur.close()
        conn.close()
        return 'saved'
    
    
    def get_selected_options_from_defense(self, session_id, name):
        conn = psycopg2.connect(**self.DB_dict)
        cur = conn.cursor(cursor_factory = DictCursor)
        
        cur.execute(SQL(""" select * from {}
                            where session_id = %(session_id)s;
                            """).format(Identifier(name)), 
                            {'session_id': session_id })
        result = cur.fetchall()
        
        conn.commit()
        cur.close()
        conn.close()
        return result


    
    
        