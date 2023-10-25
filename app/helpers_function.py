from collections import namedtuple
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
        Action('create_graph_action', 'Создать графики', QStyle.SP_ArrowRight,
               'Построить графики по отмеченным данным', None, False, 'create_normal_graph'),
        Action('play_graph_action', 'Включить движение', QStyle.SP_MediaPlay,
               'Включить/Выключить движение данных на графиках', None, True, 'play_graph'),
        Action('exit_action', 'Закрыть приложение', QStyle.SP_TitleBarCloseButton,
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
            'exit_action'
        ],
        Submenu('Графики', None): [
            'create_graph_action',
            'play_graph_action',
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
        'create_graph_action',
        'play_graph_action',
        'spin_box',
        None,
        'exit_action',
    ]
    return list_toolbar