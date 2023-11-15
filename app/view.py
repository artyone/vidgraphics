from functools import partial

import pyqtgraph as pg
from notificator import notificator
from notificator.alingments import BottomRight
from PyQt5.QtCore import QCoreApplication, Qt, QTimer
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMdiArea, QMdiSubWindow, QMenu,
                             QSlider, QSplitter, QStyle, QToolBar)
from PyQt5.sip import delete

from .controller import DataController
from .graph_window import NormalGraphWidget, VidGraphWidget
from .helpers_function import get_actions_list, get_menu_dict, get_toolbar_list
from .left_menu import Left_Menu_Tree


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.ctrl = DataController()
        self.notify: notificator = notificator()
        self.vid_graph_window = None
        self.initUI()
        self.timer = QTimer(self)
        self.timer_is_running = False
        self.timer.timeout.connect(self.update_graph_on_timer)

        # self.open_cap_file('2.pcap')

    def initUI(self) -> None:
        actions = get_actions_list()
        menu_dict = get_menu_dict()
        toolbar_list = get_toolbar_list()

        self.generate_actions(actions)
        self.generate_menu(self.menuBar(), menu_dict)
        self.generate_tool_bar(toolbar_list)
        self.create_status_bar()

        self.tree_widget = Left_Menu_Tree(self)
        self.tree_widget.hide()

        self.mdi = QMdiArea()
        self.mdi_splitter = QSplitter(Qt.Vertical)
        self.mdi_splitter.addWidget(self.mdi)
        self.mdi_splitter.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(self.mdi_splitter)

        self.setCentralWidget(self.splitter)
        self.showMaximized()

    def generate_actions(self, action_list: list) -> None:
        for action in action_list:
            setattr(self, action.name, QAction(action.title, self))
            var: QAction = getattr(self, action.name)
            if action.icon:
                var.setIcon(self.style().standardIcon(action.icon))
            var.setStatusTip(action.tip)
            if action.hotkey:
                var.setShortcut(action.hotkey)
            var.setCheckable(action.checkable)
            if isinstance(action.connect, str):
                var.triggered.connect(getattr(self, action.connect))
            if isinstance(action.connect, tuple):
                func, *args = action.connect
                func = getattr(self, func)
                var.triggered.connect(
                    partial(func, *args)
                )

    def generate_menu(self, parent_menu: QMenu, menu_dict: dict) -> None:
        for menu, actions in menu_dict.items():
            submenu: QMenu = parent_menu.addMenu(menu.title)
            if menu.icon:
                submenu.setIcon(menu.icon)
            for action in actions:
                if isinstance(action, dict):
                    self.generate_menu(submenu, action)
                elif action is None:
                    submenu.addSeparator()
                else:
                    submenu.addAction(getattr(self, action))

    def create_status_bar(self) -> None:
        '''
        Создание статус бара.
        '''
        self.statusbar = self.statusBar()
        self.statusbar.showMessage(
            'Привет, пользователь! Я за тобой слежу!', 30000
        )
        self.last_file_label = QLabel()
        self.statusbar.addPermanentWidget(self.last_file_label)

    def generate_tool_bar(self, toolbar_list: list) -> None:
        self.slider = QSlider()
        self.slider.setFixedSize(40, 100)
        self.slider.setMaximum(2000)
        self.slider.setMinimum(50)
        self.slider.setTickInterval(10)
        self.slider.setValue(300)
        self.slider.valueChanged.connect(self.slider_handler)

        position = Qt.LeftToolBarArea
        tb = QToolBar('main')
        for elem in toolbar_list:
            if elem is None:
                tb.addSeparator()
            else:
                var = getattr(self, elem)
                if isinstance(var, QAction):
                    tb.addAction(var)
                else:
                    tb.addWidget(var)
        tb.setMovable(False)
        self.addToolBar(position, tb)

    def clear_main_window(self) -> None:
        self.stop_play_graph()
        self.ctrl = DataController()
        self.tree_widget.hide()
        self.tree_widget.update_check_box()
        for window in self.mdi.subWindowList():
            window.deleteLater()
        if self.vid_graph_window:
            self.vid_graph_window.close()
        self.vid_graph_window = None


    def slider_handler(self) -> None:
        if self.timer_is_running:
            self.timer.stop()
            self.play_graph()

    def open_cap_file(self, filepath: bool | str = False) -> None:
        self.clear_main_window()
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл", "", "Pcap Files (*.pcap);;All Files (*);;")
            if not filepath:
                return

        self.ctrl.read_data_from_file(filepath)
        self.last_file_label.setText(f'Текущий файл: {self.ctrl.filepath}')
        self.tree_widget.update_check_box()

    def add_cat(self) -> None:
        pass

    def create_normal_graph(self, tree_selected=False):
        if not tree_selected:
            tree_selected = self.tree_widget.get_selected_elements()

        sub_window = QMdiSubWindow(self.mdi)
        sub_window.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_window.setWindowFlags(Qt.FramelessWindowHint)
        try:
            graph_window = NormalGraphWidget(
                self.ctrl, tree_selected, self, sub_window)
            graph_window.add_vertical_line()
        except KeyError:
            self.send_notify(
                'предупреждение',
                'Нет данных для отображения',
            )
            return

        sub_window.setWidget(graph_window)
        self.mdi.addSubWindow(sub_window)
        sub_window.show()
        self.horizontal_windows()
        self.track_graph()

    def create_vid_graph(self):
        if self.vid_graph_window is not None:
            self.vid_graph_window.set_new_data()
            return
        if self.mdi_splitter.widget(1):
            delete(self.mdi_splitter.widget(1))
        try:
            self.vid_graph_window = VidGraphWidget(
                self.ctrl, ['data_vi'], self, self.mdi_splitter)
        except KeyError:
            self.send_notify(
                'предупреждение',
                'Нет данных для отображения',
            )
            return
        self.mdi_splitter.setSizes([200, 120])
        QCoreApplication.processEvents()
        self.horizontal_windows()

    def track_graph(self) -> None:
        link = self.mdi.findChild(pg.PlotWidget)
        childs = self.mdi.subWindowList()

        for i, child in enumerate(childs, 1):
            widget = child.findChild(NormalGraphWidget)
            widget.setXLink(link)
            widget.getAxis('bottom').setStyle(showValues=False)
            if i == len(childs):
                widget.getAxis('bottom').setStyle(showValues=True)

    def update_all_vertical_line(self) -> None:
        childs = self.mdi.subWindowList()
        for child in childs:
            widget = child.findChild(NormalGraphWidget)
            widget.add_vertical_line()

    def move_all_graphics_to_vertical_line(self) -> None:
        childs = self.mdi.subWindowList()
        for child in childs:
            widget = child.findChild(NormalGraphWidget)
            widget.add_vertical_line()
            widget.move_to_vertical_line()

    def remove_all_vertical_line(self):
        childs = self.mdi.subWindowList()
        for child in childs:
            widget = child.findChild(NormalGraphWidget)
            widget.remove_vertical_line()

    def horizontal_windows(self) -> None:
        '''
        Метод для построения окон в горизональном виде.
        '''
        if not self.mdi.subWindowList():
            return
        QCoreApplication.processEvents()
        window_count = len(self.mdi.subWindowList())
        window_width = self.mdi.width()
        window_height = self.mdi.height() // window_count
        x, y = 0, 0

        for window in self.mdi.subWindowList():
            window.setGeometry(x, y, window_width, window_height)
            y += window_height

    def send_notify(self, type: str, txt: str) -> None:
        '''
        Метод отправки уведомления
        '''
        notify = self.notify.info
        duration = 5
        match type:
            case 'успех':
                notify = self.notify.sucess
            case 'ошибка':
                notify = self.notify.critical
            case _:
                notify = self.notify.warning
        notify(
            Title=type.title(),
            Message=txt,
            Parent=self,
            Align=BottomRight,
            duracion=duration,
            onclick=None
        )

    def play_graph(self):
        if self.vid_graph_window is None:
            self.create_vid_graph()
        if self.play_graph_action.isChecked():
            self.start_play_graph()
        else:
            self.stop_play_graph()

    def start_play_graph(self):
        self.play_graph_action.setChecked(True)
        self.play_graph_action.setIcon(
            self.style().standardIcon(QStyle.SP_MediaStop))
        self.timer.start(self.slider.value())
        self.timer_is_running = True

    def stop_play_graph(self):
        self.play_graph_action.setChecked(False)
        self.play_graph_action.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        self.timer.stop()
        self.timer_is_running = False

    def update_graph_on_timer(self) -> None:
        try:
            self.ctrl.set_next_time_index()
        except StopIteration:
            self.timer.stop()
            self.play_graph_action.setChecked(False)
            self.play_graph_action.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            return

        self.move_all_graphics_to_vertical_line()
        self.vid_graph_window.set_new_data()

    def go_to_next_time(self, backward=False, count=1):
        if not self.vid_graph_window:
            self.create_vid_graph()

        try:
            self.ctrl.set_next_time_index(backward, count)
        except StopIteration:
            self.send_notify('Предупреждение', 'Конец файла достигнут')
            self.update_all_vertical_line()
            return

        self.move_all_graphics_to_vertical_line()
        self.vid_graph_window.set_new_data()

    def hide_left_menu(self):
        if self.tree_widget.isVisible():
            self.tree_widget.hide()
            self.horizontal_windows()
            self.hide_left_menu_action.setChecked(True)
        else:
            self.tree_widget.show()
            self.horizontal_windows()
            self.hide_left_menu_action.setChecked(False)

    def resizeEvent(self, ev) -> None:
        self.horizontal_windows()
        return super().resizeEvent(ev)
