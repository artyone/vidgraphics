from functools import partial

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QDoubleSpinBox, QFrame, QHBoxLayout,
                             QMdiSubWindow, QMenu, QPushButton, QSlider,
                             QVBoxLayout, QWidget)
from PyQt5.sip import delete


class BaseGraphWidget(pg.PlotWidget):
    def __init__(self,
                 controller,
                 tree_selected,
                 main_window, 
                 parent,
                 background='default',
                 plotItem=None,
                 **kwargs):
        super().__init__(parent, background, plotItem, **kwargs)
        self.parent = parent
        self.ctrl = controller
        self.main_window = main_window
        self.columns: list = tree_selected
        self.data: pd.DataFrame = self.get_data()

        self.title: str = '/'.join(self.columns)
        self.colors: list = [
            'red', 'blue', 'green', 'orange',
            'gray', 'purple', 'cyan', 'yellow',
            'pink'
        ]
        self.curves: dict = dict()
        self.pos_x = 0
        self.pos_y = 0
        self.region_item = None
        self.create_graph()

    def get_data(self):
        return self.ctrl.get_data()

    def create_graph(self) -> None:
        '''
        Метод построения непосредственно самого графика
        с использованием библиотеки pyqtgraph.
        Цвета берутся по кругу из массива цветов.
        Меню библиотеки выключено. 
        При перемещении курсора выводится информация о текущем его положении.
        При правом клике мыши вызывается кастомное контекстное меню.
        '''
        if self.data is None:
            raise KeyError
        if self.columns == []:
            raise ValueError

        self.showGrid(x=True, y=True)  # показывать сетку
        self.apply_theme('white')

        for item in self.columns:
            data_for_graph = self.data.dropna(
                subset=['time', item]
            )
            data_for_graph = data_for_graph.reset_index()
            ox = data_for_graph.time.to_list()
            oy = data_for_graph[item].to_list()
            pen = pg.mkPen(color=self.colors[0], width=1.5)
            curve = pg.PlotDataItem(
                ox,
                oy,
                name=item,
                pen=pen
            )
            self.curves[f'{item}'] = {
                'curve': curve, 'pen': pen
            }
            self.addItem(curve)
            self.colors.append(self.colors.pop(0))

        self.setMenuEnabled(False)
        self.scene().sigMouseClicked.connect(self.mouse_click_event)
        self.scene().sigMouseMoved.connect(self.mouse_moved)
        self.setClipToView(True)
        self.setDownsampling(auto=True, mode='peak')

    def apply_theme(self, color):
        self.setBackground(color)
        legend_color = 'black' if color == 'white' else 'white'
        self.addLegend(
            pen=legend_color,
            labelTextColor=legend_color,
            offset=(0, 0)
        )
        pen = pg.mkPen(legend_color, width=1.0)
        self.getAxis('bottom').setPen(pen)
        self.getAxis('bottom').setTextPen(pen)
        self.getAxis('left').setPen(pen)
        self.getAxis('left').setTextPen(pen)

    def mouse_moved(self, ev):
        if self.sceneBoundingRect().contains(ev):
            mousePoint = self.getPlotItem().vb.mapSceneToView(ev)
            self.pos_x = float(mousePoint.x())
            self.pos_y = float(mousePoint.y())
            self.setWindowTitle(
                f'{self.title}       x: {round(self.pos_x, 3)}, y: {round(self.pos_y, 3)}                 '
            )
            self.setToolTip(
                f'x: <b>{round(self.pos_x, 2)}</b>,<br> y: <b>{round(self.pos_y, 2)}</b>'
            )

    def mouse_click_event(self, event) -> None:
        '''
        Метод обработки событий нажатия мышки.
        '''
        if event.button() == Qt.MouseButton.RightButton:
            self.context_menu(event)
            event.accept()
        if event.button() == Qt.MouseButton.LeftButton and event.double():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            event.accept()
        if event.button() == Qt.MouseButton.MiddleButton:
            self.close()


    def context_menu(self, event) -> None:
        '''
        Метод создания кастомного контекстного меню.
        '''
        menu = QMenu()
        self.background_menu(menu)
        self.line_type_menu(menu)

        # hide_border_window_action = QAction(
        #     '&Скрыть/показать границы окна'
        # )
        # menu.addAction(hide_border_window_action)
        # hide_border_window_action.triggered.connect(
        #     self.main_window.hide_unhide_border_window
        # )

        menu.addSeparator()

        close_action = QAction('&Закрыть')
        menu.addAction(close_action)
        close_action.triggered.connect(self.close)

        menu.exec(event.screenPos().toPoint())

    def background_menu(self, parent: QMenu) -> None:
        menu = parent.addMenu('&Фон')

        colors = {'white': 'Белый', 'black': 'Черный'}

        for encolor, rucolor in colors.items():
            action = QAction(rucolor, self)
            action.setCheckable(True)
            if getattr(self, '_background') == encolor:
                action.setChecked(True)
            else:
                action.setChecked(False)
            menu.addAction(action)
            action.triggered.connect(
                partial(self.apply_theme, encolor)
            )

    def line_type_menu(self, parent: QMenu) -> None:
        line_type = parent.addMenu('&Тип линии')
        for name, data in self.curves.items():
            line_name: QMenu = line_type.addMenu(name)  # type: ignore
            line_graph_action = QAction('&Линия', self)
            line_graph_action.setCheckable(True)
            if data['curve'].opts['pen'] == data['pen']:
                line_graph_action.setChecked(True)
            else:
                line_graph_action.setChecked(False)
            line_name.addAction(line_graph_action)
            line_graph_action.triggered.connect(
                partial(self.line_graph_event, data))

            cross_graph_action = QAction('&Точки', self)
            cross_graph_action.setCheckable(True)
            if data['curve'].opts['symbol'] is None:
                cross_graph_action.setChecked(False)
            else:
                cross_graph_action.setChecked(True)
            line_name.addAction(cross_graph_action)
            cross_graph_action.triggered.connect(
                partial(self.cross_graph_event, data))

    def line_graph_event(self, data: dict) -> None:
        '''
        Метод изменения линии графика.
        '''
        if data['curve'].opts['pen'] == data['pen']:
            data['curve'].setPen(None)
        else:
            data['curve'].setPen(data['pen'])

    def cross_graph_event(self, data: dict) -> None:
        '''
        Метод изменения линии графика.
        '''
        if data['curve'].opts['symbol'] is None:
            data['curve'].setSymbol('+')
            data['curve'].setSymbolPen(data['pen'])
        else:
            data['curve'].setSymbol(None)
    
class VidGraphWidget(BaseGraphWidget):
    def get_data(self):
        return self.ctrl.get_data(on_time_index=True)
    
class NormalGraphWidget(BaseGraphWidget):
    def mouse_click_event(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.add_vertical_line()
            self.main_window.create_vid_graph()
            event.accept()
        super().mouse_click_event(event)

    def add_vertical_line(self) -> None:
        '''
        Метод добавления вертикальной линии.
        '''
        if self.region_item is not None:
            self.removeItem(self.region_item)
            self.region_item = None
        pen = pg.mkPen('yellow', width=2)
        coordinate = self.ctrl.get_value_on_pos_x(self.pos_x)
        self.region_item = pg.InfiniteLine(
            coordinate, movable=False, pen=pen)
        self.addItem(self.region_item)
        self.main_window.update_all_vertical_line()


    def update_vertical_line(self):
        if self.region_item is not None:
            self.removeItem(self.region_item)
            self.region_item = None
        pen = pg.mkPen('yellow', width=2)
        coordinate = self.ctrl.get_value_on_pos_x()
        self.region_item = pg.InfiniteLine(
            coordinate, movable=False, pen=pen)
        self.addItem(self.region_item)


    def close(self):
        self.parent.close()
        self.main_window.horizontal_windows()
        super().close()