# This Python file uses the following encoding: utf-8
from operating.states.idle.ApplicationIdleState import ApplicationIdleState
from PySide6.QtWidgets import QSizePolicy, QPushButton, QGridLayout, QWidget, QLabel
from PySide6.QtCore import Qt, QSize, QCoreApplication




class IdleView(QWidget):
    def __init__(self, state: ApplicationIdleState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: ApplicationIdleState = state
        #===============================================

        header = QLabel(QCoreApplication.translate('Idle/view', 'Arrow'))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # header.setStyleSheet('''
        #     font-size: 25pt;
        #     font-weight: bold;
        #     font-family: Courier;
        # ''')
        button_style = "padding :5px; border: 2px solid #8f8f91;border-radius: 6px; font-size: 15pt; font-weight: bold; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #f6f7fa, stop: 1 #dadbde);"

        measuringButton = QPushButton(QCoreApplication.translate('Idle/view', 'Measuring trip'))
        measuringButton.clicked.connect(self.__state.measuring)
        # measuringButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # measuringButton.setStyleSheet(button_style)
        measuringButton.setFixedHeight(70)

        programTaskCalculattionButton = QPushButton(QCoreApplication.translate('Idle/view', 'Program task calculation'))
        programTaskCalculattionButton.clicked.connect(self.__state.programTaskCalculation)
        # programTaskCalculattionButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # programTaskCalculattionButton.setStyleSheet(button_style)
        programTaskCalculattionButton.setFixedHeight(70)

        liningButton = QPushButton(QCoreApplication.translate('Idle/view', 'Lining trip'))
        liningButton.clicked.connect(self.__state.lining)
        # liningButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # liningButton.setStyleSheet(button_style)
        liningButton.setFixedHeight(70)

        maintenanceButton = QPushButton(QCoreApplication.translate('Idle/view', 'Settings'))
        maintenanceButton.clicked.connect(self.__state.maintenance)
        # maintenanceButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # maintenanceButton.setStyleSheet(button_style)

        quitbutton = QPushButton(QCoreApplication.translate('Idle/view', 'Quit'))
        quitbutton.clicked.connect(self.__state.quit)
        # quitbutton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        # quitbutton.setStyleSheet(button_style)
        measuringButton.setProperty("optionsWindowPushButton", True)
        programTaskCalculattionButton.setProperty("optionsWindowPushButton", True)
        liningButton.setProperty("optionsWindowPushButton", True)
        maintenanceButton.setProperty("optionsWindowPushButton", True)
        quitbutton.setProperty("optionsWindowPushButton", True)



        layout = QGridLayout()
        layout.setContentsMargins(10,10,10,100)
        self.setLayout(layout)
        layout.addWidget(header, 0, 0, 1, 12, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(measuringButton, 1, 3, 1, 2)
        layout.addWidget(programTaskCalculattionButton, 1, 5, 1, 2)
        layout.addWidget(liningButton, 1, 7, 1, 2)
        layout.addWidget(maintenanceButton, 2, 3, 1, 6)
        layout.addWidget(quitbutton, 3, 3, 1, 6)


