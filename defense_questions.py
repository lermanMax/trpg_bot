from poll_module import Defense_question, get_text_from, DB


type_of_attack = Defense_question(
    'd_type_of_attack', 
    get_text_from('./questions_text/type_of_attack_for_defense.txt'),
    field_name = 'type_of_attack')


type_of_defense_1 = Defense_question(
    'type_of_defense_1', 
    get_text_from('./questions_text/type_of_defense.txt'), 
    field_name = 'type_of_defense')

type_of_defense_2 = Defense_question(
    'type_of_defense_2', 
    get_text_from('./questions_text/type_of_defense_2.txt'), 
    field_name = 'type_of_defense')

attack_weapon = Defense_question(
    'attack_weapon', 
    get_text_from('./questions_text/attack_weapon.txt'))
attack_weapon.add_options_dict(
    {'Наносит урон': None,
     'Накладывает эффект': None})

type_of_defense_3 = Defense_question(
    'type_of_defense_3', 
    get_text_from('./questions_text/type_of_defense_3.txt'), 
    field_name = 'type_of_defense')


defense_weapon_1 = Defense_question(
    'defense_weapon', 
    get_text_from('./questions_text/defense_weapon.txt'), 
    field_name = 'defense_weapon')
defense_weapon_1.add_options_dict(
    {'Щит': None,
     'Меч':None,
     'Легкий клинок':None,
     'Древковое оружие':None,
     'Рука/Нога':None})

defense_weapon_2 = Defense_question(
    'defense_weapon', 
    get_text_from('./questions_text/defense_weapon.txt'), 
    field_name = 'defense_weapon',
    column_name = 'type_of_attack', 
    required_value = 'Дистанционная')
defense_weapon_2.add_options_dict(
    {'Щит': None })

defense_weapon_3 = Defense_question(
    'defense_weapon', 
    get_text_from('./questions_text/defense_weapon.txt'), 
    field_name = 'defense_weapon')
defense_weapon_3.add_options_dict(
    {'Щит': None,
     'Меч':None,
     'Легкий клинок':None,
     'Древковое оружие':None,
     'Рука/Нога':None})


opponents = Defense_question(
    'opponents', 
    get_text_from('./questions_text/opponents.txt'), 
    field_name = 'opponents')
opponents.add_options_dict(
    {'-5 [ 6 шт.]': None,
     '-4 [ 5 шт.]':None,
     '-3 [ 4 шт.]':None,
     '-2 [ 3 шт.]':None,
     '-1 [ 2 шт.]':None,
     '-0 [0 или 1 шт.]':None})


d_mod = Defense_question(
    'd_mod', 
    get_text_from('./questions_text/mod.txt'), 
    keyboard_type = Defense_question.multiple_answer)
d_mod.add_options_dict(
    {'-2 Я сбит(а) с ног':None,
     '+1  Другой модификатор':None,
     '+2  Другой модификатор':None,
     '+3  Другой модификатор':None,
     '-1  Другой модификатор':None,
     '-2  Другой модификатор':None })

defense_failed = Defense_question(
    'defense_failed', 
    get_text_from('./questions_text/defense_failed.txt'))

def text_for_is_attack_more(session_id):
    session = DB.get_defense_session(session_id)
    
    skill_dict = {
        'Меч': 'Владение мечом',
        'Легкий клинок': 'Владение легкими клинками',
        'Древковое оружие': 'Владение древковым оружием',
        'Щит': 'Ближний бой',
        'Рука/Нога': 'Борьба' }
    
    type_of_defense = session['type_of_defense'][3:] 
    if type_of_defense == 'Уклонение/Изворот':
        parameter = 'Реакция'
        defense_weapon =''
        skill = 'Уклонение/Изворотливость'
    elif (type_of_defense == 'Изменение позиции'
          or type_of_defense == 'Уклон.[Атлетика]'):
        parameter = 'Ловкость'
        defense_weapon = ''
        skill = 'Атлетика'
    elif type_of_defense == 'Сопротивление магии':
        parameter = 'Воля'
        defense_weapon =''
        skill = 'Сопротивление магии'
    else:
        parameter = 'Реакция'
        weapon = session['defense_weapon']
        defense_weapon = f'ℹ Ваше орудие защиты: {weapon}'
        skill = skill_dict[weapon]
    
    opponents = session['opponents']
    modifier = int(opponents.split(' ')[0])
    
    list_of_modifiers = [] 
    
    list_of_modifiers.append(session['type_of_defense'])
    
    list_of_mod_rows = DB.get_selected_options_from_defense(session_id, 'd_mod')
    if list_of_mod_rows:
        for row in list_of_mod_rows:
            list_of_modifiers.append(row['value'])
    
    modifier_names = '\n'.join(list_of_modifiers)
    
    for item in list_of_modifiers:
        number = item.split(' ')[0]
        modifier += int(number)
    
    if modifier >= 0: plus = '+'
    else: plus = ''
    
    text = f'''
{defense_weapon}
ℹ Способ защиты: {type_of_defense}
    
ℹ Все модификаторы:
{opponents} противников рядом  
{modifier_names}
ℹ Сумма модификаторов: {plus}{modifier}

➡ <b>Рассчитайте защиту по формуле:</b>
Бросок D10 
+ {parameter} 
+ Навык: {skill}
{plus}{modifier}

💬 Назовите значение вашей защиты противнику 
➡ <b>Атака противника больше  вашей защиты?</b> Если да, то на сколько?
    '''
    return text

is_attack_more_1 = Defense_question(
    'd_is_attack_more_1', 
    text = text_for_is_attack_more,
    column_name = 'attack_weapon', 
    required_value = 'Накладывает эффект',
    field_name='is_attack_more')

is_attack_more = Defense_question(
    'd_is_attack_more', 
    text = text_for_is_attack_more,
    field_name='is_attack_more')


def text_for_attack_failed(session_id):
    session = DB.get_defense_session(session_id)
    
    type_of_defense = session['type_of_defense'] 
    if type_of_defense == '+0 Блокирование':
        text = '🛡 Вы отразили атаку.\n\n➡ Орудие, которым персонаж отразил атаку получает 1 урон'
    elif type_of_defense in ['-3 Парирование','-5 Парирование']:
        text = '🛡 Вы отразили атаку.\n💬 Ваш противник Ошеломлен'
    else:
        text = '🛡 Вы отразили атаку'
    return text

attack_failed = Defense_question(
    'd_attack_fail', 
    text = text_for_attack_failed)


place = Defense_question(
    'd_place', 
    get_text_from('./questions_text/place_for_defense.txt'),
    field_name='place' )
place.add_options_dict(
    {'Голова':None,
     'Туловище':None,
     'Рука':None,
     'Нога':None})


def text_for_armor(session_id):
    session = DB.get_defense_session(session_id)
    place_dict = {'Голова': 'голове',
                  'Туловище': 'туловище',
                  'Рука':'туловище (рука)',
                  'Нога':'ногах'}
    place = session['place'] 
    place_word = place_dict[place]
    
    text = f'''
➡ Введите прочность вашей брони на {place_word}
    '''
    return text

armor = Defense_question(
    'armor', 
    text=text_for_armor,
    field_name='armor',
    keyboard_type = Defense_question.numerical_answer)


def skript_for_damage_hit(session_id):
    session = DB.get_defense_session(session_id)
    additional_damage_dict = {
        'Да': 0,
        'Да, на 7-9':3,
        'Да, на 10-12':5,
        'Да, на 13-14':8,
        'Да, на 15 или больше':10}
    additional_damage = additional_damage_dict[session['is_attack_more']]
    damage_hit = session['damage_hit']
    armor = session['armor']
    answer = max(damage_hit - additional_damage - armor, 0)+ additional_damage
    
    DB.save_defense(session_id, 'damage_pierced', answer)
    
damage_hit = Defense_question(
    'd_damage_hit', 
    text=get_text_from('./questions_text/damage_hit_for_defence.txt'),
    field_name='damage_hit',
    keyboard_type = Defense_question.numerical_answer,
    skript=skript_for_damage_hit )


damage_failed = Defense_question(
    'damage_failed', 
    text=get_text_from('./questions_text/damage_failed_for_defense.txt'),
    column_name = 'damage_pierced', 
    required_value = 0)


resistance_or = Defense_question(
    'd_resistance_or', 
    get_text_from('./questions_text/resistance_or_for_defense.txt'),
    field_name='resistance_or' )
resistance_or.add_options_dict(
    {'х1/2 Сопротивление':None,
     'х2 Восприимчивость':None,
     'Нет':None})


def text_for_damage_hurt(session_id):
    session = DB.get_defense_session(session_id)
    
    place_dict = {
        'Голова': 'голове',
        'Туловище': 'туловище',
        'Рука':'туловище',
        'Нога':'ногах'}
    place = session['place'] 
    place_word = place_dict[place]
    armor = session['armor']
    
    additional_damage_dict = {
        'Да': 0,
        'Да, на 7-9':3,
        'Да, на 10-12':5,
        'Да, на 13-14':8,
        'Да, на 15 или больше':10}
    additional_damage = additional_damage_dict[session['is_attack_more']]
    damage_hit = session['damage_hit']
    armor = session['armor']
    damage_pierced = session['damage_pierced'] 
    
    modifier_place_dict = {
        'Голова': 3,
        'Туловище': 1,
        'Рука': 0.5,
        'Нога': 0.5}
    
    modifier_place = modifier_place_dict[place]
    
    resistance_or_dict = {
        'х1/2 Сопротивление': 0.5,
        'х2 Восприимчивость': 2,
        'Нет': 1}
    resistance_or_field = session['resistance_or']
    modifier_resistance_or = resistance_or_dict[resistance_or_field]
    if resistance_or_field != 'Нет':
        text_modifier_resistance_or = f"{resistance_or_field.split(' ')[1]}: {resistance_or_field.split(' ')[0]}"
    else:
        text_modifier_resistance_or = ''
    
    result_damage = damage_pierced*modifier_place*modifier_resistance_or
    
    is_attack_more_fielde = session['is_attack_more']
    if is_attack_more_fielde != 'Да':
        attack_more_defense = is_attack_more_fielde[6:]
        
        critical_level_dict = {
            'Да, на 7-9': 'Легкий',
            'Да, на 10-12': 'Средний',
            'Да, на 13-14': 'Тяжелый',
            'Да, на 15 или больше':'Смертельный'}
        critical_level = critical_level_dict[is_attack_more_fielde]
        
        crit = f'''
        
ℹ Атака превышает защиту на: {attack_more_defense}
ℹ Критический уровень: {critical_level}
    
        '''
        hurt = '\n➡ Примените критическое ранение(стр.158)'
    else: 
        crit = ''
        hurt = ''
    
    text = f'''
ℹ Место попадания: {place}

ℹ Расчет урона:
Исходный урон: {damage_hit - additional_damage} + {additional_damage}доп.урона
Прочность брони на {place_word}: {armor}
Урона преодолело броню: {damage_pierced}
Модификатор места: x{modifier_place}
{text_modifier_resistance_or} 
ℹ Получено урона: {result_damage}
{crit}
➡ <b>Учтите полученный урон</b> {hurt} 
➡ Снизьте прочность брони на 1. 
    '''
    return text

        
damage_hurt = Defense_question(
    'damage_hurt', 
    text=text_for_damage_hurt,
    field_name='damage_hurt')


# critical_injury varchar(80)


'''Defense tree----------------------------------------------------------------------------'''

type_of_attack.add_options_dict(
    {'Ближний бой': type_of_defense_1, 
     'Дистанционная': type_of_defense_2,
     'Магия': attack_weapon})

attack_weapon.next_question = type_of_defense_3

type_of_defense_1.add_options_dict(
    {'+0 Уклонение/Изворот': opponents,
     '+0 Изменение позиции': opponents,
     '+0 Блокирование': defense_weapon_2,
     '-3 Парирование': defense_weapon_1})

type_of_defense_2.add_options_dict(
    {'+0 Уклонение/Изворот': opponents,
     '+0 Изменение позиции':opponents,
     '+0 Блокирование':defense_weapon_2,
     '-5 Парирование':defense_weapon_1})

type_of_defense_3.add_options_dict(
    {'+0 Уклонение/Изворот': opponents,
     '+0 Уклон.[Атлетика]':opponents,
     '+0 Блокирование':defense_weapon_2,
     'Нет защиты': defense_failed})


defense_weapon_1.next_question = opponents
defense_weapon_2.next_question = defense_weapon_3
defense_weapon_3.next_question = opponents

opponents.next_question = d_mod

d_mod.next_question = is_attack_more_1

is_attack_more_1.next_question = is_attack_more
is_attack_more_1.add_options_dict(
    {'Нет': attack_failed,
     'Да': defense_failed})

is_attack_more.add_options_dict(
    {'Нет': attack_failed,
     'Да': place,
     'Да, на 7-9': place,
     'Да, на 10-12': place,
     'Да, на 13-14': place,
     'Да, на 15 или больше': place})

place.next_question = armor

armor.next_question = damage_hit

damage_hit.next_question = damage_failed

damage_failed.next_question = resistance_or

resistance_or.next_question = damage_hurt
