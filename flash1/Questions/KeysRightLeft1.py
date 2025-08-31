import sys
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(430, 130)
        self.centralWidget = QWidget()  # !!!
        self.setCentralWidget(self.centralWidget)  # !!!
        self.label = QLabel(self.centralWidget)
        self.label.setText('Нажмите на клавиатуре нужное вам сочетание клавиш')
        self.label.resize(400, 50)
        self.label.move(10, 10)
        self.button = QPushButton(self.centralWidget)
        self.button.setText('Создать сочетание клавиш')
        self.button.clicked.connect(self.onClicked)
        self.button.resize(400, 50)
        self.button.move(10, 50)
        self.button.setFocusPolicy(Qt.ClickFocus)  # !!!

    def keyPressEvent(self, event):
        key = event.key()
        print(f'press -> {key} -> {event.text()}')
        if key == Qt.Key_Left:
            print(f'Hello -> Key_Left')
        elif key == Qt.Key_Right:
            print(f'Hello -> Key_Right')
        self.label.setText(f'Нажмите на клавиатуре нужное вам сочетание клавиш: {event.text()}')

    def onClicked(self):
        print('Click button')
        self.setFocus()  # !!!


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())