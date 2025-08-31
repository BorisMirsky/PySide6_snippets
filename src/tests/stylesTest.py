from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
import sys

class SubWidget(QWidget):
    def __init__(self, label_text, button_text, parent_layout) -> None:
        super().__init__()

        self.setObjectName("subWidget")
        
        self.layout = QHBoxLayout()
        self.parent_layout = parent_layout
        
        self.label = QLabel(label_text)
        self.button_delete = QPushButton(button_text)
        self.button_delete.clicked.connect(self.delete_widget)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button_delete)
        self.setLayout(self.layout)

    def delete_widget(self):
        self.setParent(None)
        self.parent_layout.removeWidget(self)
        self.deleteLater()

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("mainWindow")
        self.setWindowTitle("Widget")
        self.setFixedSize(QSize(350, 500))
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        self.widget_layout = QVBoxLayout()
        self.main_layout.addLayout(self.widget_layout)

        create_label_btn = QPushButton("Create")
        self.main_layout.addWidget(create_label_btn)

        def create_label() -> None:
            new_widget = SubWidget("New Label", "Delete", self.widget_layout)
            self.widget_layout.addWidget(new_widget)

        create_label_btn.clicked.connect(create_label)

StyleSheet = """
    #mainWindow {
        background-color: darkblue;
        border-radius: 10px;
    }
    #subWidget {
        border: 2px solid black;
        margin: 5px;
        padding: 5px;
        background-color: cyan;
    }
    QPushButton {
        background-color: red;
        border: none;
        padding: 5px;
    }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    window = MainWindow()
    window.show()
    app.exec()
