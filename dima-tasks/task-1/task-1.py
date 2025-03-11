"""
Следующие две строки нужны для запуска этого скрипта
в терминале из текущей директории.
Это связано с тем, что модуль core находится
в другой директории (не в текущей).
"""
import sys

sys.path.append("../../")

from src.core import UserAccount
from task_1_helper import TestCase, run_tests


def print_user_account(person):
    print(f'username - {person.username}, password - {person.password}')


def task_1a(x, y):
    psn = UserAccount(x, y)
    print_user_account(psn)


task_1a('DM', '888')


def task_1b(account_lst):
    for i in account_lst:
        print_user_account(i)


task_1b([(UserAccount(i, i + 100)) for i in range(1, 7)])


def is_normal_username(username):
    if username[0].isalpha() and len(username) >= 3:
        return True if username.isalpha() or username.isalnum() else False
    return False

t_dict = {
    'aaaaa': True,
    '1ooooo': False,
    'DA': False,
    'DD***XXX': False,
    'GGG': True,
    '#dghhgfds': False
}

run_tests(is_normal_username, [TestCase(x, y) for x, y in t_dict.items()])

