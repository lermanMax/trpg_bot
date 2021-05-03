from poll_module import Attack_question, get_text_from, DB


'''Attack '''

type_of_attack = Attack_question('type_of_attack', 
                                 get_text_from('./questions_text/type_of_attack.txt'))


melee_weapon = Attack_question('melee_weapon', 
                                get_text_from('./questions_text/melee_weapon.txt'), 
                                keyboard_type = Attack_question.one_answer, 
                                options_dict = None, 
                                column_name = None, 
                                required_value = None,
                                next_question=None)
melee_weapon.add_options_dict({'Меч': None,
                               'Легкий клинок': None,
                               'Древковое оружие': None,
                               'Щит': None,
                               'Рука/Нога': None})


ranged_weapon = Attack_question('ranged_weapon', 
                                get_text_from('./questions_text/ranged_weapon.txt'))



fast_or_hard_1 = Attack_question('fast_or_hard_1', 
                                 get_text_from('./questions_text/fast_or_hard.txt'))
fast_or_hard_1.add_options_dict({'+0 Быстро [2 атаки]': None,
                                 '-3 Сильно': None})
  
fast_or_hard_2 = Attack_question('fast_or_hard_2', 
                                get_text_from('./questions_text/fast_or_hard.txt'))
fast_or_hard_2.add_options_dict({'+0 Обычно [1 атака]': None,
                                '-3 Сильно': None})

fast_or_hard_3 = Attack_question('fast_or_hard_3', 
                                get_text_from('./questions_text/fast_or_hard.txt'))
fast_or_hard_3.add_options_dict({'+0 Обычно [1 атака]': None})


place_penalty = Attack_question('place_penalty', 
                                get_text_from('./questions_text/place_penalty.txt'))
place_penalty.add_options_dict({'-6 Голова': None,
                                '-1 Туловище': None,
                                '-3 Рука/Конечность': None,
                                '-2 Нога/Крыло/Хвост': None,
                                '+0 Случайное место': None})


distance = Attack_question('distance', 
                           get_text_from('./questions_text/distance.txt'),
                           column_name = 'type_of_attack', 
                           required_value = 'Дистанционная')
distance.add_options_dict({'+5 В упор [<0.5 метра]': None,
                           '+0 Близкая [1/4 дистанции]': None,
                           '-2 Средняя [1/2 дистанции]': None,
                           '-4 Дальняя [1х дистанция]': None,
                           '-6 Экстрем. [2х дистанция]': None})



mod = Attack_question('mod', 
                      get_text_from('./questions_text/mod.txt'), 
                      keyboard_type = Attack_question.multiple_answer)
mod.add_options_dict({'+3  Я вне конуса зрения Ц':None,
                      '-3 Ц вне моего конуса зрения':None,
                      '+4  Ц обездвижена':None,
                      '-2  Ц уклоняется':None,
                      '-3  Ц движется, ее Реа>10':None,
                      '-3  Быстрое выхватывание':None,
                      '+5  Засада':None,
                      '-5  Рикошет':None,
                      '-2  Я сбит(а) с ног':None,
                      '-3  Ослеплен(а) светом/пылью':None,
                      '-2  Темнота':None,
                      '+2  Ц на контрастном фоне':None,
                      '-3 Это доп. действие':None,
                      '+1  Другой модификатор':None,
                      '+2  Другой модификатор':None,
                      '+3  Другой модификатор':None
                      })



weapon_accuracy = Attack_question('weapon_accuracy', 
                                  get_text_from('./questions_text/weapon_accuracy.txt'))
weapon_accuracy.add_options_dict({'+5': None,
                                  '+4': None,
                                  '+3': None,
                                  '+2': None,
                                  '+1': None,
                                  '+0': None})


effects = Attack_question('effects', 
                          get_text_from('./questions_text/effects.txt'), 
                          keyboard_type = Attack_question.multiple_answer)
effects.add_options_dict({'-1 Замораживание':None,
                          '-2 Ошеломление':None,
                          '-2 Опьянение':None,
                          '-3 Слепота':None})


def text_for_attack_more(session_id):
    
    session = DB.get_attack_session(session_id)
    
    skill_dict = {'Меч': 'Владение мечом',
                  'Легкий клинок': 'Владение легкими клинками',
                  'Древковое оружие': 'Владение древковым оружием',
                  'Щит': 'Ближний бой',
                  'Рука/Нога': 'Борьба',
                  'Метательное': 'Атлетика',
                  'Лук': 'Стрельба из лука',
                  'Арбалет': 'Стрельба из арбалета'}
    
    if session['type_of_attack'] == 'Дистанционная':
        parameter = 'Ловкость'
        weapon = session['ranged_weapon']
        skill = skill_dict[weapon]
    else:
        parameter = 'Реакция'
        weapon = session['melee_weapon']
        skill = skill_dict[weapon]
    
    accuracy = session['weapon_accuracy']
    
    modifier = int(accuracy)
    list_of_modifiers = []
    
    if (session['fast_or_hard_1'] == '-3 Сильно' 
        or session['fast_or_hard_2'] == '-3 Сильно'):
        list_of_modifiers.append('-3 Сильная атака')
    
    list_of_modifiers.append(session['place_penalty'])
    
    if session['distance']: list_of_modifiers.append(session['distance'])
    
    list_of_mod_rows = DB.get_selected_options_from_attack(session_id, 'mod')
    if list_of_mod_rows:
        for row in list_of_mod_rows:
            list_of_modifiers.append(row['value'])
    
    list_of_effects_rows = DB.get_selected_options_from_attack(session_id, 'effects')
    if list_of_effects_rows:
        for row in list_of_effects_rows:
            list_of_modifiers.append(row['value'])
    
    modifier_names = '\n'.join(list_of_modifiers)
    
    for item in list_of_modifiers:
        number = item.split(' ')[0]
        modifier += int(number)
    
    if modifier >= 0: plus = '+'
    else: plus = '' 
    text = f'''
ℹ Ваше оружие атаки: {weapon}
    
ℹ Все модификаторы:
{accuracy} Точность оружия  
{modifier_names}
ℹ Сумма модификаторов = {plus}{modifier}

➡ Рассчитайте атаку по формуле:
Бросок D10 
+ {parameter} 
+ Навык: {skill}
{plus}{modifier}

💬 Назовите значение вашей атаки противнику 
➡ Ваша атака больше защиты противника?
    '''
    return text


is_attack_more = Attack_question('is_attack_more', 
                                  text = text_for_attack_more)

attack_failed = Attack_question(
    'attack_failed', 
    get_text_from('./questions_text/attack_failed.txt'))

body = Attack_question('body',
                       get_text_from('./questions_text/body.txt'))
body.add_options_dict({'-4 [Тел. 1-2]': None,
                       '-2 [Тел. 3-4]': None,
                       '+0 [Тел. 5-6]': None,
                       '+2 [Тел. 7-8]': None,
                       '+4 [Тел. 9-10]': None,
                       '+6 [Тел. 11-12]': None,
                       '+8 [Тел. 13-20]': None})


weapon_damage = Attack_question(
    'weapon_damage', 
    get_text_from('./questions_text/weapon_damage.txt'), 
    keyboard_type = Attack_question.numerical_answer)


enemy_type = Attack_question('enemy_type', 
                             get_text_from('./questions_text/enemy_type.txt'),
                             column_name = 'place_penalty', 
                             required_value = '+0 Случайное место')

place_humanoid = Attack_question('place_humanoid', 
                                 get_text_from('./questions_text/place_humanoid.txt'))
place_humanoid.add_options_dict({'1 Голова': None,
                                 '2-4 Туловище': None,
                                 '5 Правая рука': None,
                                 '6 Левая рука': None,
                                 '7-8 Правая нога ': None,
                                 '9-10 Левая нога': None})


place_monster = Attack_question('place_monster', 
                                get_text_from('./questions_text/place_monster.txt'))
place_monster.add_options_dict({'1 Голова': None,
                                '2-5 Туловище': None,
                                '6-7 Правая конечность': None,
                                '8-9 Левая конечность': None,
                                '10 Хвост/крыло': None})


def text_for_damage_more(session_id):
    session = DB.get_attack_session(session_id)
    
    additional_damage_dict = {'Да': 0,
                              'Да, на 7-9':3,
                              'Да, на 10-12':5,
                              'Да, на 13-14':8,
                              'Да, на 15 или больше':10}
    
    if session['type_of_attack'] == 'Дистанционная':
        weapon = session['ranged_weapon']
    else:
        weapon = session['melee_weapon']
    
    if session['place_penalty'] == '+0 Случайное место':
        if session['place_humanoid']:
            place_list = session['place_humanoid'].split(' ')[1:]
        else:
            place_list = session['place_monster'].split(' ')[1:]
    else:
        place_list = session['place_penalty'].split(' ')[1:]
        
    place = ' '.join(place_list)
    
    weapon_damage = session['weapon_damage']
    result_damage = weapon_damage
    
    if session['fast_or_hard_1'] != None:
        body_damage = session['body'].split(' ')[0]
        result_damage += int(body_damage)
        plus_body = f'Добавить телосложение: {body_damage}\n' 
    else:
        plus_body = ''
    
    if (session['fast_or_hard_1'] == '-3 Сильно' 
        or session['fast_or_hard_2'] == '-3 Сильно'):
        result_damage = result_damage * 2
        x_strong_attack = 'Сильная атака: Урон х2 \n'
    else:
        x_strong_attack = ''
    
    additional_damage = additional_damage_dict[session['is_attack_more']]
    if additional_damage != 0:
        result_damage += additional_damage
        plus_additional_damage = f'Дополнительный урон: {additional_damage}\n'
        comment_additional_damage = '(Доп. урон не блокируется броней)'
        comment_result = f'({result_damage - additional_damage} + {additional_damage}доп.урона)'
    else:
        plus_additional_damage = ''
        comment_additional_damage = ''
        comment_result = ''
    
    text = f'''
ℹ Ваше оружие атаки: {weapon}
ℹ Место попадания: {place}

ℹ Расчет урона:
Выпавший на кубах урон оружия: {weapon_damage}
{plus_body}{x_strong_attack}{plus_additional_damage}    
ℹ Итоговый урон: {result_damage} {comment_result}

💬 Назовите место попадания, урон и тип урона противнику {comment_additional_damage}
➡ Урон преодолел броню?
    '''
    
    return text

is_damage_more = Attack_question('is_damage_more', 
                                text = text_for_damage_more)

damage_failed = Attack_question(
    'damage_failed', 
    get_text_from('./questions_text/damage_failed.txt'))

damage_hit = Attack_question(
    'damage_hit', 
    get_text_from('./questions_text/damage_hit.txt'), 
    keyboard_type = Attack_question.numerical_answer)

 
resistance_or = Attack_question('resistance_or', 
                                get_text_from('./questions_text/resistance_or.txt'))
resistance_or.add_options_dict({'х1/2 Сопротивление': None,
                                'х2 Восприимчивость': None,
                                'Нет': None})


def text_for_damage_hurt(session_id):
    session = DB.get_attack_session(session_id)
    
    modifier_place_dict = {'1 Голова': 3,
                           '2-4 Туловище': 1,
                           '5 Правая рука': 0.5,
                           '6 Левая рука': 0.5,
                           '7-8 Правая нога ': 0.5,
                           '9-10 Левая нога': 0.5,
                           '1 Голова': 3,
                           '2-5 Туловище': 1,
                           '6-7 Правая конечность': 0.5,
                           '8-9 Левая конечность': 0.5,
                           '10 Хвост/крыло': 0.5,
                           '-6 Голова': 3,
                           '-1 Туловище': 1,
                           '-3 Рука/Конечность': 0.5,
                           '-2 Нога/Крыло/Хвост': 0.5}
    
    resistance_or_dict = {'х1/2 Сопротивление': 0.5,
                          'х2 Восприимчивость': 2,
                          'Нет': 1}
    
    damage = session['damage_hit']
    
    if session['place_penalty'] == '+0 Случайное место':
        if session['place_humanoid']:
            place_field = session['place_humanoid']
        else:
            place_field = session['place_monster']
    else:
        place_field = session['place_penalty']
    place = ' '.join(place_field.split(' ')[1:])
    
    modifier_place = modifier_place_dict[place_field]
    
    resistance_or_field = session['resistance_or']
    modifier_resistance_or = resistance_or_dict[resistance_or_field]
    if resistance_or_field != 'Нет':
        text_modifier_resistance_or = f"{resistance_or_field.split(' ')[1]}: {resistance_or_field.split(' ')[0]}"
    else:
        text_modifier_resistance_or = ''
    
    result_damage = damage*modifier_place*modifier_resistance_or
    
    if session['is_attack_more'] == 'Да': finish = '⚔ Вы завершили атаку'
    else: finish = '➡ Нажмите "Далее" чтобы определить критическое ранения'
    
    text = f'''
ℹ Расчет урона:
Урона преодолело броню: {damage}
Место попадания: {place}
Модификатор места: x{modifier_place}
{text_modifier_resistance_or} 
ℹ Нанесенный урон противнику: {result_damage}

💬 Назовите нанесенный урон противнику

{finish}
    '''
    return text


damage_hurt_finish = Attack_question(
    'damage_hurt_finish', 
    text = text_for_damage_hurt,
    column_name = 'is_attack_more', 
    required_value = 'Да')

damage_hurt = Attack_question(
    'damage_hurt', 
    text = text_for_damage_hurt)


critical_injury = Attack_question('critical_injury', 
                                get_text_from('./questions_text/critical_injury.txt'))
critical_injury.add_options_dict(
    {'12': None,
     '11': None,
     '9-10': None,
     '6-8': None,
     '4-5': None,
     '2-3': None})



def text_for_critical_description(session_id):
    session = DB.get_attack_session(session_id)
    
    is_attack_more_fielde = session['is_attack_more']
    attack_more_defense = is_attack_more_fielde[6:]
    
    critical_level_dict = {
        'Да, на 7-9': 'Легкий',
        'Да, на 10-12': 'Средний',
        'Да, на 13-14': 'Тяжелый',
        'Да, на 15 или больше':'Смертельный'}
    critical_level = critical_level_dict[is_attack_more_fielde]
    
    critical_injury_roll = session['critical_injury']
    
    critical_effect_name = '[тут будет название эффекта]'
    critical_effect = '[тут будет описание эффекта]'
    critical_stabilization = '[тут будет описнаие эффекта после стабилизации]'
    critical_healing = '[тут будет описание эффекта после лечения]'
    
    text = f'''    
ℹ Атака превышает защиту на: {attack_more_defense}
ℹ Критический уровень: {critical_level}

ℹ Результат броска 2d6: {critical_injury_roll}
ℹ Эффект: {critical_effect_name}
{critical_effect}

ℹ После стабилизации:
{critical_stabilization}

ℹ После лечения: 
{critical_healing}
    
💬 Назовите описание противнику (или перешлите это сообщение)

[раздел в разработке. опиание критических ранений ищите в книге на стр.158]
    '''
    return text


critical_description = Attack_question(
    'critical_description', 
    text = text_for_critical_description)



'''Attack tree----------------------------------------------------------------------------'''

type_of_attack.add_options_dict({'Ближний бой':melee_weapon, 
                                 'Дистанционная':ranged_weapon})
melee_weapon.next_question = fast_or_hard_1

ranged_weapon.add_options_dict({'Метательное': fast_or_hard_1,
                                'Лук': fast_or_hard_2,
                                'Арбалет': fast_or_hard_3})

fast_or_hard_1.next_question = place_penalty
fast_or_hard_2.next_question = place_penalty
fast_or_hard_3.next_question = place_penalty

place_penalty.next_question = distance

distance.next_question = mod

mod.next_question = weapon_accuracy

weapon_accuracy.next_question = effects

effects.next_question = is_attack_more

is_attack_more.add_options_dict({'Нет': attack_failed,
                                 'Да': body,
                                 'Да, на 7-9': body,
                                 'Да, на 10-12': body,
                                 'Да, на 13-14': body,
                                 'Да, на 15 или больше': body})


body.next_question = weapon_damage

weapon_damage.next_question = enemy_type

enemy_type.add_options_dict({'Гуманоид': place_humanoid,
                             'Монстр': place_monster})
enemy_type.next_question = is_damage_more

place_humanoid.next_question = is_damage_more

place_monster.next_question = is_damage_more

is_damage_more.add_options_dict({'Да': damage_hit,
                                 'Нет': damage_failed})

damage_hit.next_question = resistance_or

resistance_or.next_question = damage_hurt_finish

damage_hurt_finish.next_question = damage_hurt

damage_hurt.add_options_dict({'Далее': critical_injury})

critical_injury.next_question = critical_description
