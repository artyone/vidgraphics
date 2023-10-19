import sys

from PyQt5.QtWidgets import QApplication, QMainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main_window = QMainWindow()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()