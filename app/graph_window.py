from functools import partial

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMenu


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
        self.getAxis('left').setWidth(50)
        self.create_graph()

    def get_data(self):
        return self.ctrl.get_data_main()

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
        self.apply_theme('black')
        self.setMenuEnabled(False)
        self.scene().sigMouseClicked.connect(self.mouse_click_event)
        self.scene().sigMouseMoved.connect(self.mouse_moved)
        self.setClipToView(True)
        self.setDownsampling(auto=True, mode='peak')

        for item in self.columns:
            data_for_graph = self.data.dropna(
                subset=['time', item]).reset_index()
            ox = data_for_graph.time.to_list()
            oy = data_for_graph[item].to_list()
            pen = pg.mkPen(color=self.colors[0], width=1.5)
            curve = pg.PlotDataItem(ox, oy, name=item, pen=pen)
            self.curves[f'{item}'] = {'curve': curve, 'pen': pen}
            self.addItem(curve)
            self.colors.append(self.colors.pop(0))

        self.display_text = pg.TextItem(text='',color=(255,255,255),anchor=(-0.1, 1))
        self.addItem(self.display_text)
  
    def apply_theme(self, color):
        self.setBackground(color)
        legend_color = 'black' if color == 'white' else 'white'
        pen = pg.mkPen(legend_color, width=1.0)
        for axis in ['bottom', 'left']:
            axis_obj = self.getAxis(axis)
            axis_obj.setPen(pen)
            axis_obj.setTextPen(pen)
        self.addLegend(
            pen=legend_color,
            labelTextColor=legend_color,
            offset=(0, 0)
        )

    def mouse_moved(self, ev):
        if self.sceneBoundingRect().contains(ev):
            mousePoint = self.getPlotItem().vb.mapSceneToView(ev)
            self.getPlotItem().vb.disableAutoRange()
            self.pos_x = float(mousePoint.x())
            self.pos_y = float(mousePoint.y())
            self.display_text.setPos(self.pos_x,self.pos_y)
            self.display_text.setText(f'y: {self.pos_y:.2f}') #x: {self.pos_x:.2f}, 
            self.clear_other_display_text()

    def clear_other_display_text(self):
        childs = self.main_window.mdi.subWindowList()
        for i, child in enumerate(childs, 1):
            widget = child.findChild(NormalGraphWidget)
            if widget is not self:
                widget.display_text.setText('')

    def mouse_click_event(self, event) -> None:
        '''
        Метод обработки событий нажатия мышки.
        '''
        if event.button() == Qt.MouseButton.RightButton:
            self.context_menu(event)
            event.accept()

        elif (
            event.button() == Qt.MouseButton.LeftButton
            and event.double()
            and event.modifiers() != Qt.KeyboardModifier.ControlModifier
        ):
            self.showNormal() if self.isMaximized() else self.showMaximized()
            event.accept()

        elif event.button() == Qt.MouseButton.MiddleButton:
            event.accept()
            self.close()

    def context_menu(self, event) -> None:
        '''
        Метод создания кастомного контекстного меню.
        '''
        menu = QMenu()
        self.create_background_menu(menu)
        self.create_line_type_menu(menu)

        menu.addSeparator()

        close_action = QAction('&Закрыть')
        menu.addAction(close_action)
        close_action.triggered.connect(self.close)

        menu.exec(event.screenPos().toPoint())

    def create_background_menu(self, parent: QMenu) -> None:
        menu = parent.addMenu('&Фон')

        colors = {'white': 'Белый', 'black': 'Черный'}

        for encolor, rucolor in colors.items():
            action = QAction(rucolor, self)
            action.setCheckable(True)
            action.setChecked(getattr(self, '_background') == encolor)
            menu.addAction(action)
            action.triggered.connect(partial(self.apply_theme, encolor))

    def create_line_type_menu(self, parent: QMenu) -> None:
        line_type = parent.addMenu('&Тип линии')
        for name, data in self.curves.items():
            line_name: QMenu = line_type.addMenu(name)  # type: ignore
            line_graph_action = QAction('&Линия', self)
            line_graph_action.setCheckable(True)
            line_graph_action.setChecked(
                data['curve'].opts['pen'] == data['pen'])
            line_name.addAction(line_graph_action)
            line_graph_action.triggered.connect(
                partial(self.line_graph_event, data)
            )

            cross_graph_action = QAction('&Точки', self)
            cross_graph_action.setCheckable(True)
            cross_graph_action.setChecked(
                data['curve'].opts['symbol'] is not None)
            line_name.addAction(cross_graph_action)
            cross_graph_action.triggered.connect(
                partial(self.cross_graph_event, data)
            )

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
        return self.ctrl.get_data_vi()

    def set_new_data(self) -> None:
        data = self.get_data()
        self.curves['data_vi']['curve'].setData(data.time, data['data_vi'])

    def close(self):
        self.main_window.vid_graph_window = None
        self.hide()
        self.main_window.horizontal_windows()
        self.main_window.remove_all_vertical_line()
        self.deleteLater()


class NormalGraphWidget(BaseGraphWidget):
    def mouse_click_event(self, event) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.add_vertical_line(self.pos_x)
            self.main_window.update_all_vertical_line()
            self.main_window.create_vid_graph()
            event.accept()
        super().mouse_click_event(event)

    def add_vertical_line(self, pos_x=None) -> None:
        '''
        Метод добавления вертикальной линии.
        '''
        if self.region_item:
            self.removeItem(self.region_item)
            self.region_item = None
        pen = pg.mkPen('yellow', width=2)
        if pos_x:
            coordinate = self.ctrl.get_value_on_pos_x(pos_x)
        else:
            coordinate = self.ctrl.get_value_on_pos_x()
        self.region_item = pg.InfiniteLine(coordinate, movable=False, pen=pen)
        self.addItem(self.region_item)

    def move_to_vertical_line(self):
        coordinate = self.ctrl.get_value_on_pos_x()
        xrange = self.viewRange()[0]
        raz = coordinate - (xrange[0] + xrange[1]) / 2
        self.setXRange(xrange[0] + raz, xrange[1] + raz, padding=0)

    def remove_vertical_line(self):
        if self.region_item is not None:
            self.removeItem(self.region_item)
            self.region_item = None

    def close(self):
        self.parent.close()
        self.main_window.horizontal_windows()
        super().close()
