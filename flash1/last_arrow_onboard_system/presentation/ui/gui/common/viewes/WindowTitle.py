# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt
from resources.style.StyleManager import StyleManager
import configparser

class Window(QVBoxLayout):
    def __init__(self, 
                 title:str = None,
                 parent: QWidget = None ) ->None:
        super().__init__(parent)

        self.setContentsMargins(0,0,0,0)
        #self.setLayout(self.__window)

        self.__title = WindowTitle(title=title)
        self.addWidget(self.__title)

    def setTitle(self, title:str) -> None:
        self.__title.setText(title)


class WindowTitle(QWidget):
    def __init__(self, 
                 title:str = None,
                 parent: QWidget = None ) ->None:
        super().__init__(parent)

         # Чтение версии сборки из конфигурационного файла
        config = configparser.ConfigParser()
        config.read("build_version.ini", "utf-8")
        build_version = config.get("App", "build_version", fallback="Версия неизвестна")


        self.__title = title
        self.__label = QLabel(self.__title) 
        self.__parent = parent

        layout =  QHBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.__label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__label.setStyleSheet(StyleManager.window_title())
        layout.addWidget(self.__label, 1)

        # Заголовок версии сборки
        self.__version_label = QLabel(f"Сборка: {build_version}")
        self.__version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.__version_label.setStyleSheet(StyleManager.window_title_version() + StyleManager.window_title())
        #self.__version_label.setStyleSheet(StyleManager.window_title())
        
        layout.addWidget(self.__version_label)

    def setText(self, title:str) -> None:
        self.__title = title
        self.__label.setText(self.__title)