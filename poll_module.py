import types

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from db_module import DB_module

# Data base
DB = DB_module(DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT)


def get_text_from(path):
    with open(path,'r') as file:
        one_string = ''
        for line in file.readlines():
            one_string += line
    return one_string
            

class Attack_question:
    '''
    Шаблон вопроса для опроса по теме атаки
    '''
    
    # словарь из имен вопросов и ссылок на объекты с этим вопросом
    all_questions = {}
    # Текст на кнопке [дальше]
    next_button_name = 'Дальше'
    
    one_answer = 'one'
    multiple_answer = 'multiple'
    numerical_answer = 'numerical'
    
    numerical_options = [1,2,3,4,5,6,7,8,9,10]
    increase_numbers = '>>'
    decrease_numbers = '<<'
    
    end = 'end_of_poll'
    
    def __init__(self, name, text=None, 
                 keyboard_type = one_answer,
                 field_name = None,
                 options_dict = None, 
                 column_name = None, required_value = None,
                 skript = None,
                 next_question=None):
        
        Attack_question.all_questions[name] = self
        
        self.name = name
        self.add_field(field_name)
        self.column_name = column_name
        self.required_value = required_value
        self.text = text
        self.keyboard_type = keyboard_type
        self.skript = skript
        self.next_question = next_question
        self.add_options_dict(options_dict)
            
        
    def add_field(self, field_name):
        if not field_name:
            self.field_name = self.name
        else:
            self.field_name = field_name
        return
    
    
    def add_options_dict(self, options_dict):
        if not options_dict: 
            if self.keyboard_type == Attack_question.numerical_answer:
                self.options_dict = self.get_numerical_options()
            elif self.keyboard_type == Attack_question.multiple_answer:
                self.options_dict = {
                    Attack_question.next_button_name: self.next_question}
            else:
                self.options_dict = None
                return 
            
        elif self.keyboard_type == Attack_question.one_answer:
            self.options_dict = options_dict
        elif self.keyboard_type == Attack_question.multiple_answer:
            self.options_dict = options_dict
            self.options_dict[Attack_question.next_button_name] = self.next_question
        else:
            raise Exception("something wrong in attribute 'keyboard_type' ")
    
    
    def get_all_questions_list():
        return [key for key in Attack_question.all_questions]
            
    
    def get_numerical_options(self, k=0):
        options = {x+k:None for x in Attack_question.numerical_options}
        options[Attack_question.decrease_numbers] = None
        options[Attack_question.increase_numbers] = None
        return options
    
    
    def get_text(self, session_id):
        if isinstance(self.text, str): 
            return self.text
        elif isinstance(self.text, types.FunctionType):
            return self.text(session_id)
        else:
            raise Exception("something wrong in attribute 'text' ")
    
    
    def get_options_list(self, k=0):
        if self.keyboard_type == Attack_question.numerical_answer:
            result = [x+k for x in Attack_question.numerical_options]
            result.append(Attack_question.decrease_numbers)
            result.append(Attack_question.increase_numbers)
            return result
        elif not self.options_dict:
            return None
        else:
            return [key for key in self.options_dict]
    
    
    def _is_relevant(self, session_id):
        if not self.column_name: return True
        
        attack_session = DB.get_attack_session(session_id)
        if attack_session[self.column_name] == self.required_value: 
            return True
        else:
            return False
    
    
    def save_option(self, session_id, answer):
        if self.keyboard_type == Attack_question.multiple_answer:
            DB.save_attack_multiple_answer(session_id, self.field_name, answer)    
        else:
            DB.save_attack(session_id, self.field_name, answer)
    
    
    def get_selected_options(self, session_id):
        if self.keyboard_type == Attack_question.multiple_answer:
            rows = DB.get_selected_options_from_attack(session_id, self.name)
            return [row['value'] for row in rows ] 
        else:
            return None
    
    def do_skript(self, session_id):
        if isinstance(self.skript, types.FunctionType):
            self.skript(session_id)
        else:
            return
    
    def get_next_question(self, session_id, answer=None):
        if not answer: 
            next_q = self.next_question #default next question
        elif self.options_dict[answer]:
            '''Есть ли точный адрес в зависимости от ответа'''
            next_q = self.options_dict[answer]
        else:
            next_q = self.next_question #default next question
        
        if not next_q:
            return None
        elif next_q._is_relevant(session_id):
            return next_q
        else:
            return next_q.get_next_question(session_id)
        
        
    def next_data_for_button(self, answer, k=0):
        if answer == Attack_question.increase_numbers:
            return k+10        
        elif answer == Attack_question.decrease_numbers:
            return k-10
        else:
            return 0
        
    
    def next_step(self, session_id, answer):
        '''
        Главный метод. 
        
        Сохраняет ответы.
        Говорит что делать дальше:
            + Переходить к следующему вопросу
            + Сохронить ответ и выдать этот-же вопрос
        '''
        if self.keyboard_type == Attack_question.one_answer:
            self.save_option(session_id, answer)
            self.do_skript(session_id)
            return self.get_next_question(session_id, answer)
        
        elif self.keyboard_type == Attack_question.multiple_answer:
            if answer == Attack_question.next_button_name:
                self.do_skript(session_id)
                return self.get_next_question(session_id, answer)
            else:
                self.save_option(session_id, answer)
                return self
            
        elif self.keyboard_type == Attack_question.numerical_answer:
            if (answer == Attack_question.increase_numbers 
                or answer == Attack_question.decrease_numbers):
                return self
            else:
                self.save_option(session_id, answer)
                self.do_skript(session_id)
                return self.get_next_question(session_id)
                

class Defense_question:
    '''
    Шаблон вопроса для опроса по теме ЗАЩИТА
    '''
    
    # словарь из имен вопросов и ссылок на объекты с этим вопросом
    all_questions = {}
    # Текст на кнопке [дальше]
    next_button_name = 'Дальше'
    
    one_answer = 'one'
    multiple_answer = 'multiple'
    numerical_answer = 'numerical'
    
    numerical_options = [1,2,3,4,5,6,7,8,9,10]
    increase_numbers = '>>'
    decrease_numbers = '<<'
    
    def __init__(self, name, text=None, 
                 keyboard_type = one_answer,
                 field_name = None,
                 options_dict = None, 
                 column_name = None, required_value = None,
                 skript = None,
                 next_question=None):
        
        Defense_question.all_questions[name] = self
        
        self.name = name
        self.add_field(field_name)
        self.column_name = column_name
        self.required_value = required_value
        self.text = text
        self.keyboard_type = keyboard_type
        self.skript = skript
        self.next_question = next_question
        self.add_options_dict(options_dict)
            
        
    def add_field(self, field_name):
        if not field_name:
            self.field_name = self.name
        else:
            self.field_name = field_name
        return
    
    
    def add_options_dict(self, options_dict):
        if not options_dict: 
            if self.keyboard_type == Defense_question.numerical_answer:
                self.options_dict = self.get_numerical_options()
            elif self.keyboard_type == Defense_question.multiple_answer:
                self.options_dict = {
                    Defense_question.next_button_name: self.next_question}
            else:
                self.options_dict = None
                return 
            
        elif self.keyboard_type == Defense_question.one_answer:
            self.options_dict = options_dict
        elif self.keyboard_type == Defense_question.multiple_answer:
            self.options_dict = options_dict
            self.options_dict[Defense_question.next_button_name] = self.next_question
        else:
            raise Exception("something wrong in attribute 'keyboard_type' ")
    
    
    def get_all_questions_list():
        return [key for key in Defense_question.all_questions]
            
    
    def get_numerical_options(self, k=0):
        options = {x+k:None for x in Defense_question.numerical_options}
        options[Defense_question.decrease_numbers] = None
        options[Defense_question.increase_numbers] = None
        return options
    
    
    def get_text(self, session_id):
        if isinstance(self.text, str): 
            return self.text
        elif isinstance(self.text, types.FunctionType):
            return self.text(session_id)
        else:
            raise Exception("something wrong in attribute 'text' ")
    
    
    def get_options_list(self, k=0):
        if self.keyboard_type == Defense_question.numerical_answer:
            result = [x+k for x in Defense_question.numerical_options]
            result.append(Defense_question.decrease_numbers)
            result.append(Defense_question.increase_numbers)
            return result
        elif not self.options_dict:
            return None
        else:
            return [key for key in self.options_dict]
    
    
    def _is_relevant(self, session_id):
        if not self.column_name: return True
        
        attack_session = DB.get_defense_session(session_id)
        if attack_session[self.column_name] == self.required_value: 
            return True
        else:
            return False
    
    
    def save_option(self, session_id, answer):
        if self.keyboard_type == Defense_question.multiple_answer:
            DB.save_defense_multiple_answer(session_id, self.field_name, answer)    
        else:
            DB.save_defense(session_id, self.field_name, answer)
    
    
    def get_selected_options(self, session_id):
        if self.keyboard_type == Defense_question.multiple_answer:
            rows = DB.get_selected_options_from_defense(session_id, self.name)
            return [row['value'] for row in rows ] 
        else:
            return None
    
    def do_skript(self, session_id):
        if isinstance(self.skript, types.FunctionType):
            self.skript(session_id)
        else:
            return
    
    def get_next_question(self, session_id, answer=None):
        if not answer: 
            next_q = self.next_question #default next question
        elif self.options_dict[answer]:
            '''Есть ли точный адрес в зависимости от ответа'''
            next_q = self.options_dict[answer]
        else:
            next_q = self.next_question #default next question
        
        if not next_q:
            return None
        elif next_q._is_relevant(session_id):
            return next_q
        else:
            return next_q.get_next_question(session_id)
        
        
    def next_data_for_button(self, answer, k=0):
        if answer == Defense_question.increase_numbers:
            return k+10        
        elif answer == Defense_question.decrease_numbers:
            return k-10
        else:
            return 0
        
    
    def next_step(self, session_id, answer):
        '''
        Главный метод. 
        Сохраняет ответы.
        Говорит что делать дальше:
            1. Переходить к следующему вопросу
            2. Сохронить ответ и выдать этот-же вопрос
        '''
        if self.keyboard_type == Defense_question.one_answer:
            self.save_option(session_id, answer)
            self.do_skript(session_id)
            return self.get_next_question(session_id, answer)
        
        elif self.keyboard_type == Defense_question.multiple_answer:
            if answer == Defense_question.next_button_name:
                self.do_skript(session_id)
                return self.get_next_question(session_id, answer)
            else:
                self.save_option(session_id, answer)
                return self
            
        elif self.keyboard_type == Defense_question.numerical_answer:
            if (answer == Defense_question.increase_numbers 
                or answer == Defense_question.decrease_numbers):
                return self
            else:
                self.save_option(session_id, answer)
                self.do_skript(session_id)
                return self.get_next_question(session_id)

        
