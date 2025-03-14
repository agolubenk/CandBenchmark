# vacancies/utils.py

CURRENCY_SYNONYMS = {
    'usd': 'USD',
    'доллар': 'USD',
    '$': 'USD',
    'rub': 'RUB',
    'руб': 'RUB',
    'rub.': 'RUB',
    'rur': 'RUB',
    'руб.': 'RUB',
    'byn': 'BYN',
    'br': 'BYN',
    'belrub': 'BYN',
    'byn.': 'BYN',
    'евро': 'EUR',
    '€': 'EUR',
    'eur': 'EUR',
    'зарк': 'ZAR',    # Если у вас встречаются какие-то опечатки
    'zar': 'ZAR',
    # ... при необходимости добавляйте другие варианты ...
}

VALID_CURRENCIES = {'USD', 'RUB', 'BYN', 'EUR', 'ZAR'}

def unify_currency(input_str):
    """
    Приводит значение валюты к одному из списка VALID_CURRENCIES (например, 'USD', 'RUB'...).
    Если не находит в словаре синонимов, возвращает input_str.upper().
    """
    if not input_str:
        return ''
    norm = input_str.lower().strip()
    # Ищем в словаре
    if norm in CURRENCY_SYNONYMS:
        return CURRENCY_SYNONYMS[norm]
    # Иначе fallback
    upper_code = norm.upper()
    if upper_code in VALID_CURRENCIES:
        return upper_code
    return upper_code   # либо 'UNKNOWN', или ''


#
# Грейды
#
GRADE_SYNONYMS = {
    'intern': 'trainee',
    'стажер': 'trainee',
    'стажёр': 'trainee',
    'джуниор': 'junior',
    'jun': 'junior',
    'мидл': 'middle',
    'сеньор': 'senior',
    # ... и т.п.
}

VALID_BASE_GRADES = {'trainee', 'junior', 'middle', 'senior', 'lead', 'head'}

def unify_grade(input_grade):
    """
    Приводит строку грейда к формату:
      - Переводим базовый грейд в Trainee / Junior / Middle / Senior / Lead / Head
      - Сохраняем суффикс + или - (например, "Senior+", "Junior-")
    Если не удается сопоставить, оставляем как есть.
    """
    if not input_grade:
        return ''
    norm = input_grade.lower().strip()
    suffix = ''
    # Если заканчивается на + или -, «отделим» этот знак
    if norm.endswith('+') or norm.endswith('-'):
        suffix = norm[-1]   # '+' или '-'
        norm = norm[:-1].strip()  # убираем символ, обрезаем пробелы

    # Проверяем словарь синонимов
    if norm in GRADE_SYNONYMS:
        norm = GRADE_SYNONYMS[norm]

    # Теперь проверяем, есть ли norm в VALID_BASE_GRADES
    if norm not in VALID_BASE_GRADES:
        # Если нет, можно либо вернуть исходную строку, либо ''
        return input_grade  # fallback
    # Делаем первую букву заглавной, остальные строчные
    canonical = norm.capitalize()  # trainee->Trainee, middle->Middle, lead->Lead
    return canonical + suffix  # Добавляем приписку + или -