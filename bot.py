import asyncio
import logging
import typing

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import callback_data, exceptions

from config import API_TOKEN, admin_id
from poll_module import get_text_from, Attack_question, Defense_question, DB
import attack_questions
import defense_questions

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('messages_sender')

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# sructure of callback bottons 
button_cb = callback_data.CallbackData('B', 
                                       'q_name', 'ans', 's_id', 'data')

attack_message = '⚔ Я АТАКУЮ!'
defense_message = '🛡 Я ЗАЩИЩАЮСЬ'
help_message = 'Помощь'
basemenu_list = [attack_message, defense_message, help_message]

all_attack_list = Attack_question.get_all_questions_list()
all_defense_list = Defense_question.get_all_questions_list()
all_list = all_attack_list + all_defense_list

def make_keyboard(question_name, keyboard_type, session_id, 
                  answers, selected_answers = None, next_button_name=None,
                  data = 0):
    """ Возвращает клавиатуру """
    if not answers: return None
    if not selected_answers: selected_answers = []
    
    one_answer = 'one'
    multiple_answer = 'multiple'
    numerical_answer = 'numerical'
    
    selected = '🔳'
    unselected = '◻'

    keyboard = types.InlineKeyboardMarkup()
    
    if keyboard_type == one_answer:    
        for answer in answers: # make a botton for every answer 
            cb_data=button_cb.new(q_name = question_name,
                                  ans = answer,
                                  s_id = session_id,
                                  data = data)
            button = types.InlineKeyboardButton(answer,
                                                callback_data=cb_data)
            keyboard.row(button)
    
    elif keyboard_type == multiple_answer:  
        for answer in answers: # make a botton for every answer 
            cb_data=button_cb.new(q_name = question_name,
                                  ans = answer,
                                  s_id = session_id,
                                  data = data)
            if answer in selected_answers:
                button = types.InlineKeyboardButton(selected + answer,
                                                    callback_data=cb_data)
            elif answer == next_button_name:
                button = types.InlineKeyboardButton(answer,
                                                    callback_data=cb_data)
            else:
                button = types.InlineKeyboardButton(unselected + answer,
                                                    callback_data=cb_data)
            keyboard.row(button)
    
    elif keyboard_type == numerical_answer:
        list_of_buttons = []
        for answer in answers: # make a botton for every answer 
            cb_data=button_cb.new(q_name = question_name,
                                  ans = answer,
                                  s_id = session_id,
                                  data = data)
            list_of_buttons.append(types.InlineKeyboardButton(answer,
                                                  callback_data=cb_data))
        
        keyboard.row(*list_of_buttons[:5])
        keyboard.row(*list_of_buttons[5:10])
        keyboard.row(*list_of_buttons[10:])
    
    else:
        raise Exception("something wrong with keyboard_type in maker")
        
    return keyboard


def get_basemenu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in basemenu_list: keyboard.add(types.KeyboardButton(name))
    return keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logging.info('start command from: %r', message.from_user.id) 
    
    DB.add_user(message.from_user.id, 
                message.from_user.first_name, 
                message.from_user.last_name, 
                message.from_user.username, 
                message.from_user.language_code)

    keyboard = get_basemenu_keyboard()
    text = get_text_from('./questions_text/hello.txt')
    await message.answer(text, reply_markup = keyboard)    


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    logging.info('help command from: %r', message.from_user.id) 
    keyboard = get_basemenu_keyboard()
    await message.answer(get_text_from('./questions_text/help.txt'), 
                         reply_markup=keyboard)

    
@dp.callback_query_handler(button_cb.filter(q_name=all_list))
async def callback_button(query: types.CallbackQuery, 
                          callback_data: typing.Dict[str, str]):
    """ Юзер нажимает на кнопку под вопросом"""
    # callback_data contains all info from callback data
    logging.info('Got this callback data: %r', callback_data) 
    
    await query.answer()  # don't forget to answer callback query as soon as possible
    from_user = query.from_user.id
    callback_question_name = callback_data['q_name']
    callback_answer = callback_data['ans']
    callback_session_id = callback_data['s_id']
    callback_ans_data = int(callback_data['data'])
    
    if callback_question_name in all_attack_list:
        previous_question = Attack_question.all_questions[callback_question_name]
        next_button_name = Attack_question.next_button_name
    elif callback_question_name in all_defense_list:
        previous_question = Defense_question.all_questions[callback_question_name]
        next_button_name = Defense_question.next_button_name
    else:   
        raise Exception("WTF? question not in lists")
        
    question = previous_question.next_step(callback_session_id, callback_answer)
    if not question: return
        
    question_name = question.name
    text = question.get_text(callback_session_id)
    data = previous_question.next_data_for_button(callback_answer, callback_ans_data)
    answers = question.get_options_list(data)
    keyboard = make_keyboard(question_name, 
                             question.keyboard_type,
                             callback_session_id,
                             answers,
                             question.get_selected_options(callback_session_id),
                             next_button_name,
                             data)
    
    await bot.edit_message_text(text,
                                from_user,
                                query.message.message_id,
                                reply_markup=keyboard )
            
        
@dp.message_handler(lambda message: message.text in basemenu_list)
async def base_menu(message: types.Message):
    """
    Получаем нажатие кнопки из базового меню
    Запускаем соответствующие процесс:
        Атака
        Защита
    """
    logging.info('push basemenu button from: %r', message.from_user.id)
    if message.text == attack_message:
        session_id = DB.new_attack_session(message.from_user.id)
        
        question_name = 'type_of_attack'
        question = Attack_question.all_questions[question_name]
        text = question.get_text(session_id)
        answers = question.get_options_list()
        keyboard = make_keyboard(question_name, 
                                 question.keyboard_type,
                                 session_id,
                                 answers)
        await message.answer(text, reply_markup = keyboard )
    elif message.text == defense_message:
        # await message.answer('[раздел в разработке, попробуйте атаку]')
        session_id = DB.new_defense_session(message.from_user.id)
        
        question_name = 'first_d'
        question = Defense_question.all_questions[question_name]
        text = question.get_text(session_id)
        answers = question.get_options_list()
        keyboard = make_keyboard(question_name, 
                                 question.keyboard_type,
                                 session_id,
                                 answers)
        await message.answer(text, reply_markup = keyboard )
        
    elif message.text == help_message:
        await send_help(message)
    return 



@dp.message_handler(content_types = types.message.ContentType.TEXT)
async def new_text_message(message: types.Message):
    """
    Принимает текстовые сообщения
    Перенаправляем админу 
    """
    for _id in admin_id:
        user_row = DB.get_user(message.from_user.id)
        text = '/n'.join(user_row)
        await bot.send_message(_id, text + message.text)
    await message.reply('Я передам эту информацию разработчикам. Спасибо!')
    

@dp.message_handler(content_types = types.message.ContentType.ANY)
async def staf(message: types.Message):
    """ любой другой контент просто отметаем"""
    logging.info('strange staf from: %r', message.from_user.id)
    await message.reply(get_text_from('./questions_text/wtf.txt'))



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)