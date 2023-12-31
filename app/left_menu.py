from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (QApplication, QMenu, QTreeWidget, QTreeWidgetItem,
                             QTreeWidgetItemIterator)


class Left_Menu_Tree(QTreeWidget):
    '''Виджет для отображения списка данных в виде дерева'''

    def __init__(self, parent) -> None:
        '''__init__

        Args:
            parent (view.MainWindow): основное окно программы
        '''
        super().__init__()
        self.parent = parent
        self.setColumnCount(2)
        self.setHeaderLabels(['Название', 'Количество'])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.handle_item_click)

    def update_check_box(self) -> None:
        """
        Обновляет виджет дерева с помощью данных полученных от контроллера.

        Returns:
            None
        """
        headers: list = self.parent.ctrl.get_headers_for_left_menu()
        if headers is None:
            self.hide()
            return
        self.hide()
        self.clear()
        headers.sort(key=lambda x: x[0])
        for name, count in headers:
            tree_item = QTreeWidgetItem(self)
            tree_item.setText(0, name)
            tree_item.setText(1, str(count))
            tree_item.setFont(1, QFont('Arial', 8, 1, True))
            if count:
                tree_item.setForeground(1, QColor('gray'))
            else:
                tree_item.setForeground(1, QColor('red'))
            tree_item.setFlags(tree_item.flags() | Qt.ItemIsUserCheckable)
            tree_item.setCheckState(0, Qt.Unchecked)

        self.show()
        self.resize_columns_to_contents()
        self.parent.splitter.setSizes([90, 500])

    def resize_columns_to_contents(self) -> None:
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    @staticmethod
    def get_info_item(item: QTreeWidgetItem) -> list:
        """
        Возвращает информацию о элементе дерева.
        """
        info = []
        # Так как глубина дерева 3, то получаем максимум 3 элемента
        for _ in range(3):
            if item:
                info.append(item.text(0))
            else:
                break
            item = item.parent()
        return info[::-1]

    def handle_item_click(self, item: QTreeWidgetItem, _) -> None:
        """
        Обработка двойного клика на элементе дерева. 
        """
        mouse_event = QApplication.mouseButtons()
        if mouse_event == Qt.LeftButton:
            self.parent.create_normal_graph([item.text(0)])

    def show_context_menu(self, position: QPoint) -> None:
        """
        Отображает контекстное меню с различными действиями на основе текущего выбранного элемента.

        Args:
            - position (QPoint): Позиция курсора в дереве.

        Returns:
            - None.
        """
        menu = QMenu(self)
        uncheck_all_action = menu.addAction('Снять все отметки')
        uncheck_all_action.triggered.connect(self.update_check_box)

        menu.exec_(self.viewport().mapToGlobal(position))

    def get_selected_elements(self) -> list:
        '''
        Фукнция для получения всех отмеченных чек-боксов.
        '''
        selected_elements = []
        iterator = QTreeWidgetItemIterator(
            self, QTreeWidgetItemIterator.Checked
        )
        while iterator.value():
            item = iterator.value()
            selected_elements.append(item.text(0))
            iterator += 1
        return selected_elements
