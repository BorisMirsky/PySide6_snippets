# This Python file uses the following encoding: utf-8
from InformationLabel import InformationLabelClass
from Tab import TabClass
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from AbstractModels import AbstractReadModel
from MockModels import SinMockModel


class MainClass(QWidget):
    def __init__(self,
                 sensor1: AbstractReadModel[float],
                 sensor2: AbstractReadModel[float],
                 sensor3: AbstractReadModel[float],
                 sensor4: AbstractReadModel[float],
                 timer: QTimer(),
                 parent: QWidget = None) -> None:
        super().__init__(parent)
        insertionTimer = timer
        top_panel = InformationLabelClass(sensor1,sensor2,sensor3,sensor4)
        tab = TabClass(sensor1,sensor2,sensor3,sensor4, insertionTimer)
        #table = TableClass([0,sensor1,sensor2,sensor3,sensor4], insertionTimer)
        vbox = QVBoxLayout(self)
        vbox.addWidget(top_panel)
        vbox.addWidget(tab)
        self.setLayout(vbox)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    sensor1 = SinMockModel(amplitude=5, frequency=2, parent=app)
    sensor2 = SinMockModel(amplitude=4, frequency=3, parent=app)
    sensor3 = SinMockModel(amplitude=3, frequency=4, parent=app)
    sensor4 = SinMockModel(amplitude=2, frequency=5, parent=app)
    timer = QTimer()
    #
    # Вот тут надо создать и показать (show) виджет
    #top_panel = InformationLabelClass(sensor_1,sensor_2,sensor_3,sensor_4)
    #top_panel.show()
    #
    #tab = TabClass(sensor_1,sensor_2,sensor_3,sensor_4, timer)
    #tab.show()
    #
    main = MainClass(sensor1,sensor2,sensor3,sensor4, timer)
    main.show()
    sys.exit(app.exec())
