from functools import partial

import pyqtgraph as pg
from notificator import notificator
from notificator.alingments import BottomRight
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMdiArea, QMdiSubWindow, QMenu,
                             QSplitter, QToolBar)
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

        # temp
        # self.open_cap_file('test.cap')

    def initUI(self) -> None:
        self.generate_actions(get_actions_list())
        self.generate_menu(self.menuBar(), get_menu_dict())
        self.generate_tool_bar(get_toolbar_list())
        self.create_status_bar()
        self.mdi = QMdiArea()

        self.splitter = QSplitter(Qt.Horizontal)

        self.tree_widget = Left_Menu_Tree(self.ctrl, self)
        self.tree_widget.hide()
        self.splitter.addWidget(self.tree_widget)

        self.mdi_splitter = QSplitter(Qt.Vertical)
        self.mdi_splitter.addWidget(self.mdi)
        self.mdi_splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.mdi_splitter)

        self.setCentralWidget(self.splitter)
        # self.showMaximized()

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
        position = Qt.LeftToolBarArea
        toolbar = QToolBar('main')
        for elem in toolbar_list:
            if elem is None:
                toolbar.addSeparator()
                continue
            var = getattr(self, elem)
            if isinstance(var, QAction):
                toolbar.addAction(var)
            else:
                toolbar.addWidget(var)
        toolbar.setMovable(False)
        self.addToolBar(position, toolbar)

    def clear_main_window(self):
        self.ctrl = DataController()
        self.tree_widget.clear()
        self.tree_widget.hide()
        for window in self.mdi.subWindowList():
            window.deleteLater()
        self.vid_graph_window.close()
        self.vid_graph_window = None

    def open_cap_file(self, filepath=False):
        if filepath is False:
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл", "",
                "Pcap Files (*.pcap);;All Files (*);;", options=options
            )
        if filepath:
            self.ctrl.read_data_from_file(filepath)
            self.last_file_label.setText(
                f'Текущий файл: {self.ctrl.filepath}'
            )
            self.tree_widget.update_check_box()

    def add_cat(self):
        pass

    def create_normal_graph(self, custom_selected=False):
        tree_selected = custom_selected if custom_selected else self.tree_widget.get_selected_elements()
        sub_window = QMdiSubWindow(self.mdi)
        sub_window.setAttribute(Qt.WA_DeleteOnClose, True)
        sub_window.setWindowFlags(Qt.FramelessWindowHint)
        try:
            graph_window = NormalGraphWidget(
                self.ctrl, tree_selected, self, sub_window)
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
        if self.vid_graph_window is None:
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
            return
        self.vid_graph_window.set_new_data()
        

    def track_graph(self):
        link = self.mdi.findChild(pg.PlotWidget)
        childs = self.mdi.subWindowList()
        for child in childs:
            widget = child.findChild(NormalGraphWidget)
            widget.setXLink(link)
            widget.getAxis('bottom').setStyle(showValues=False)
        last_child = childs[-1].findChild(NormalGraphWidget)
        last_child.getAxis('bottom').setStyle(showValues=True)

    def update_all_vertical_line(self):
        childs = self.mdi.subWindowList()
        for child in childs:
            widget = child.findChild(NormalGraphWidget)
            widget.update_vertical_line()

    def horizontal_windows(self) -> None:
        '''
        Метод для построения окон в горизональном виде.
        '''
        if not self.mdi.subWindowList():
            return
        QCoreApplication.processEvents()
        width = self.mdi.width()
        heigth = self.mdi.height() // len(self.mdi.subWindowList())
        pnt = [0, 0]
        for window in self.mdi.subWindowList():
            window.setGeometry(pnt[0], pnt[1], width, heigth)
            pnt[1] += heigth

    def send_notify(self, type: str, txt: str) -> None:
        '''
        Метод отправки уведомления
        '''
        notify = self.notify.info
        duration = 10
        if type == 'предупреждение':
            notify = self.notify.warning
        if type == 'успех':
            notify = self.notify.sucess
            duration = 5
        if type == 'ошибка':
            notify = self.notify.critical
        notify(
            Title=type.title(),
            Message=txt,
            Parent=self,
            Align=BottomRight,
            duracion=duration,
            onclick=None
        )
    def resizeEvent(self, ev) -> None:
        self.horizontal_windows()
        return super().resizeEvent(ev)
