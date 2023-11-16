from collections import namedtuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyle


def get_actions_list() -> list:
    """
    Описатель actions

    Returns:
        list: список для создания actions
    """
    Action = namedtuple(
        'action', [
            'name', 'title', 'icon', 'tip', 'hotkey', 'checkable', 'connect'
        ]
    )
    list_action = [
        Action('clear_all_action', 'Очистить окно', None,
               'Очистить все данные в программе.', None, False, 'clear_main_window'),
        Action('open_cap_file_action', 'Открыть *.cap', QStyle.SP_FileIcon,
               'Открыть cap файл с данными.', None, False, 'open_cap_file'),
        Action('open_dir_action', 'Открыть *.cap', QStyle.SP_DirIcon,
               'Открыть директорию с данными.', None, False, 'open_dir'),
        Action('create_graph_action', 'Создать графики', QStyle.SP_DialogYesButton,  # QStyle.SP_ArrowRight
               'Построить графики по отмеченным данным', None, False, 'create_normal_graph'),
        Action('play_graph_action', 'Включить движение', QStyle.SP_MediaPlay,
               'Включить/Выключить движение данных на графиках', Qt.Key_Space, True, 'play_graph'),
        Action('go_to_next_time_action', 'Следующий кадр', QStyle.SP_MediaSeekForward,
               'Переключиться на следующий кадр', None, False, ('go_to_next_time', False, 1)),
        Action('go_to_back_time_action', 'Предыдущий кадр', QStyle.SP_MediaSeekBackward,
               'Переключиться на предыдущий кадр', None, False, ('go_to_next_time', True, 1)),
        Action('go_to_next_time_500_action', 'Следующая секунда', QStyle.SP_MediaSkipForward,
               'Переключиться на кадр следующей секунды', 'Right', False, ('go_to_next_time', False, 500)),
        Action('go_to_back_time_500_action', 'Предыдущая секунда', QStyle.SP_MediaSkipBackward,
               'Переключиться на кадр предыдущей секунды', 'Left', False, ('go_to_next_time', True, 500)),
        Action('hide_left_menu_action', 'Скрыть левое меню', QStyle.SP_DialogResetButton,
               'Скрыть/показать левое меню', None, True, 'hide_left_menu'),
        Action('exit_action', 'Закрыть приложение', QStyle.SP_LineEditClearButton,
               'Закрыть приложение навсегда', 'Ctrl+Q', False, 'close'),
        Action('about_action', 'О программе', None,
               'О программе', None, False, 'add_cat')
    ]
    return list_action


def get_menu_dict() -> dict:
    """
    Описатель меню

    Returns:
        dict: словарь для создания меню
    """
    Submenu = namedtuple('submenu', ['title', 'icon'])
    menu_dict = {
        Submenu('Файл', None): [
            'clear_all_action',
            'open_cap_file_action',
            'open_dir_action',
            'hide_left_menu_action',
            'exit_action'
        ],
        Submenu('Графики', None): [
            'create_graph_action',
            'play_graph_action',
            'go_to_next_time_action',
            'go_to_back_time_action',
            'go_to_next_time_500_action',
            'go_to_back_time_500_action',
        ],
        Submenu('Настройки', None): [
            'about_action'
        ]
    }
    return menu_dict


def get_toolbar_list() -> list:
    """
    Описатель тулбара

    Returns:
        list: список для создания тулбара
    """
    list_toolbar = [
        'open_cap_file_action',
        'open_dir_action',
        'create_graph_action',
        'play_graph_action',
        'slider',
        'go_to_next_time_action',
        'go_to_back_time_action',
        'go_to_next_time_500_action',
        'go_to_back_time_500_action',
        'hide_left_menu_action',
        None,
        'exit_action',
    ]
    return list_toolbar
