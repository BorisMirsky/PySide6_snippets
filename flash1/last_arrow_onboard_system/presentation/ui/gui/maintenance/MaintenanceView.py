# This Python file uses the following encoding: utf-8
from operating.states.maintenance.ApplicationMaintenanceState import ApplicationMaintenanceState
from presentation.ui.gui.common.viewes.WindowTitle import Window

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt, QCoreApplication

class MaintenanceView(QWidget):
    def __init__(self, state: ApplicationMaintenanceState, parent: QWidget = None):
        super().__init__(parent)
        self.__state: ApplicationMaintenanceState = state
        self.__window = Window("Настройки")
        #===============================================

        maintenanceCompleteButton = QPushButton('Выход')
        maintenanceCompleteButton.clicked.connect(self.__state.maintenanceCompleted)
        maintenanceCompleteButton.setProperty("optionsWindowPushButton", True)
        controlRideButton = QPushButton('Контрольный заезд')
        controlRideButton.clicked.connect(self.__controlRide)
        controlRideButton.setProperty("optionsWindowPushButton", True)
        sensorsCalibrationButton = QPushButton('Тарировка датчиков')
        sensorsCalibrationButton.clicked.connect(self.__sensorsCalibration)
        sensorsCalibrationButton.setProperty("optionsWindowPushButton", True)

        layout = QVBoxLayout()
        self.__window.addLayout(layout, 1)
        self.setLayout(self.__window)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(QCoreApplication.translate('Maintenance/error/view', 'Maintenance mode is not ready...')))
        layout.addWidget(controlRideButton)
        layout.addWidget(sensorsCalibrationButton)
        layout.addWidget(maintenanceCompleteButton)


    def __controlRide(self):               # self.__state.__controlRide
        pass

    def __sensorsCalibration(self):       # self.__state.__sensorsCalibration
        pass

