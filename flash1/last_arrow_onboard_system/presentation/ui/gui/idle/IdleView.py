# This Python file uses the following encoding: utf-8
import os
import configparser

from PySide6.QtGui import QFontDatabase, QFont, QPixmap

from operating.states.idle.ApplicationIdleState import ApplicationIdleState
from PySide6.QtWidgets import QSizePolicy, QPushButton, QGridLayout, QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QApplication
from PySide6.QtCore import Qt, QSize, QCoreApplication, QTimer

from resources.style.StyleManager import StyleManager
from tools.helpers import ButtonFactory
from presentation.ui.gui.common.viewes.WindowTitle import WindowTitle



class IdleView(QWidget):
    def __init__(self, state: ApplicationIdleState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: ApplicationIdleState = state
        #===============================================

        # Чтение версии сборки из конфигурационного файла
        config = configparser.ConfigParser()
        config.read("build_version.ini", "utf-8")
        build_version = config.get("App", "build_version", fallback="Версия неизвестна")

        # Установка глобального стиля
        self.setStyleSheet(StyleManager.menu_button_style())
        self.custom_font = StyleManager.load_font()

        # Заголовок версии сборки
        version_label = QLabel(f"Сборка: {build_version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet(StyleManager.window_title_version())
        version_label.setFont(self.custom_font)

        # Логотип
        self.logo_label = QLabel()
        self.original_pixmap = QPixmap("resources/images/logo_vniizht_strela.png")
        if not self.original_pixmap.isNull():
            self.logo_label.setPixmap(self.original_pixmap.scaled(800, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                                                  Qt.TransformationMode.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        else:
            self.logo_label.setText("[Ошибка загрузки логотипа]")
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_label.setFont(self.custom_font)

        # Кнопки
        buttons = [
            ("Measuring trip", self.__state.measuring),
            ("Program task calculation", self.__state.programTaskCalculation),
            ("Lining trip", self.__state.lining),
            ("Settings", self.__state.maintenance),
            ("Quit", self.__state.quit)
        ]
        button_widgets = [
            ButtonFactory.create_button(QCoreApplication.translate('Idle/view', text), callback, self.custom_font)
            for text, callback in buttons]


        # Макет
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        button_layout = QGridLayout()
        
        
        top_layout.addWidget(version_label)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.logo_label)
        main_layout.addLayout(button_layout)

        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setSpacing(10)

        # 1 row
        button_layout.addWidget(button_widgets[0], 0, 0, 1, 2)
        button_layout.addWidget(button_widgets[1], 0, 2, 1, 2)
        button_layout.addWidget(button_widgets[2], 0, 4, 1, 2)
        # 2 row
        button_layout.addWidget(button_widgets[3], 1, 0, 1, 3)
        button_layout.addWidget(button_widgets[4], 1, 3, 1, 3)

        self.setLayout(main_layout)
        if QApplication.instance():
            QApplication.instance().focusChanged.connect(self.update_button_focus)
        QTimer.singleShot(0, self.set_initial_focus)  # Принудительно передаёт фокус первой кнопке

        self.setMinimumSize(800, 800)

    def set_initial_focus(self):
        """Принудительно передаёт фокус первой кнопке"""
        if hasattr(self, 'button_widgets') and self.button_widgets:
            self.button_widgets[0].setFocus()

    def update_button_focus(self):
        """Обновляет стиль активной кнопки в IdleView"""
        buttons = self.findChildren(QPushButton)  # Находим все кнопки внутри IdleView

        for button in buttons:
            if button.hasFocus():
                button.setStyleSheet(StyleManager.active_menu_button_style())
            else:
                button.setStyleSheet(StyleManager.menu_button_style())  # Сбрасываем стиль

        self.repaint()



# ====================================================================
#          header = QLabel(QCoreApplication.translate('Idle/view', 'Arrow'))
        # header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # # header.setStyleSheet('''
        # #     font-size: 25pt;
        # #     font-weight: bold;
        # #     font-family: Courier;
        # # ''')
        # button_style = "padding :5px; border: 2px solid #8f8f91;border-radius: 6px; font-size: 15pt; font-weight: bold; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);"
        #
        # measuringButton = QPushButton(QCoreApplication.translate('Idle/view', 'Measuring trip'))
        # measuringButton.clicked.connect(self.__state.measuring)
        # # measuringButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # # measuringButton.setStyleSheet(button_style)
        # measuringButton.setFixedHeight(70)
        #
        # programTaskCalculattionButton = QPushButton(QCoreApplication.translate('Idle/view', 'Program task calculation'))
        # programTaskCalculattionButton.clicked.connect(self.__state.programTaskCalculation)
        # # programTaskCalculattionButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # # programTaskCalculattionButton.setStyleSheet(button_style)
        # programTaskCalculattionButton.setFixedHeight(70)
        #
        # liningButton = QPushButton(QCoreApplication.translate('Idle/view', 'Lining trip'))
        # liningButton.clicked.connect(self.__state.lining)
        # # liningButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # # liningButton.setStyleSheet(button_style)
        # liningButton.setFixedHeight(70)
        #
        # maintenanceButton = QPushButton(QCoreApplication.translate('Idle/view', 'Settings'))
        # maintenanceButton.clicked.connect(self.__state.maintenance)
        # # maintenanceButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # # maintenanceButton.setStyleSheet(button_style)
        #
        # quitbutton = QPushButton(QCoreApplication.translate('Idle/view', 'Quit'))
        # quitbutton.clicked.connect(self.__state.quit)
        # # quitbutton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # # quitbutton.setStyleSheet(button_style)
        # measuringButton.setProperty("optionsWindowPushButton", True)
        # programTaskCalculattionButton.setProperty("optionsWindowPushButton", True)
        # liningButton.setProperty("optionsWindowPushButton", True)
        # maintenanceButton.setProperty("optionsWindowPushButton", True)
        # quitbutton.setProperty("optionsWindowPushButton", True)
        #
        #
        #
        # layout = QGridLayout()
        # layout.setContentsMargins(10,10,10,100)
        # self.setLayout(layout)
        # layout.addWidget(header, 0, 0, 1, 12, Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(measuringButton, 1, 3, 1, 2)
        # layout.addWidget(programTaskCalculattionButton, 1, 5, 1, 2)
        # layout.addWidget(liningButton, 1, 7, 1, 2)
        # layout.addWidget(maintenanceButton, 2, 3, 1, 6)
        # layout.addWidget(quitbutton, 3, 3, 1, 6)

