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
    print_user_account(psn)


task_1a('DM', '888')


def task_1b(account_lst) :
    for i in account_lst:
        print(f'username = {i.username}, password = {i.password}')


task_1b( [(UserAccount( i, i+100)) for i in range(1, 7)] )

