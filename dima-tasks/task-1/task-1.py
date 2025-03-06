"""
Следующие две строки нужны для запуска этого скрипта
в терминале из текущей директории.
Это связано с тем, что модуль core находится
в другой директории (не в текущей).
"""
import sys
sys.path.append( "../../" )

from src.core import UserAccount


def print_user_account(person) :
    print(f'username - {person.username}, password - {person.password}')


def task_1a(x, y) :
    psn = UserAccount(x, y)
    return psn


print_user_account(task_1a('Don Pedro', 'Pedro_777'))


def task_1b() :
    pass