from PySide6.QtWidgets import QFrame, QWidget, QApplication, QVBoxLayout, QStackedLayout, QPushButton
from PySide6.QtCore import Qt


class ColorWidget(QFrame):
    def __init__(self, color):
        super(ColorWidget, self).__init__()
        self.setFixedSize(200, 200)

        self.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        # Some widget. In this case, just a colored background.


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.current_widget = False

        layout = QStackedLayout(self)
        layout.addWidget(ColorWidget("red"))
        layout.addWidget(ColorWidget("yellow"))
        layout.setCurrentIndex(0)

        # Main widget. Contains 2 colored widgets.

    def change_visible_widget(self):
        self.current_widget = not self.current_widget
        self.layout().setCurrentIndex(int(self.current_widget))


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # no frame, no background

        layout = QVBoxLayout()
        main_widget = MainWidget()
        button = QPushButton("change")
        button.clicked.connect(main_widget.change_visible_widget)
        # button to change QStackedLayout index in Main Widget

        layout.addWidget(main_widget)
        layout.addWidget(button)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication()
    win = MainWindow()
    win.show()
    app.exec()