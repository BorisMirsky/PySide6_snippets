from PySide6.QtWidgets import (QWidget, QLabel,QGridLayout,QSpinBox,QRadioButton,QPushButton,QLineEdit,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox)
#from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, Qt, QColor, QDoubleValidator
from PySide6.QtCore import Qt, QObject, QCoreApplication
import sys

# background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
#                                   stop: 0 #E0E0E0, stop: 1 #FFFFFF);

groupbox_style = """
            QGroupBox {
                border: 2px solid #999999;
                border-radius: 5px;
                margin-top: 1ex;  
                font-size: 15px;
                font-weight: bold;
                color: black;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;    
                padding: 0 3px;
                font-size: 13px;
                color: black;
            }
        """


class Main(QWidget):
    def __init__(self):
        super().__init__()
        #
        top_label = QLabel("Установки ограничений")
        top_label.setStyleSheet("font-size: 18px;font-weight: bold;")
        top_label.setAlignment(Qt.AlignCenter)
        #
        groupbox1_title = "Скорости км/ч"
        groupbox1 = QGroupBox(groupbox1_title, alignment=Qt.AlignHCenter)
        groupbox1.setStyleSheet(groupbox_style)
        groupbox1_grid = QGridLayout()
        groupbox1_grid_label1 = QLabel("Макс. пассажирским")
        groupbox1_grid_label2 = QLabel("Макс. грузовым")
        groupbox1_grid_label3 = QLabel("Уклон отвода м/мм")
        groupbox1_grid_spinbox1 = QSpinBox()
        groupbox1_grid_spinbox1.setRange(0,1000000)
        groupbox1_grid_spinbox2 = QSpinBox()
        groupbox1_grid_spinbox2.setRange(0, 1000000)
        groupbox1_grid_lineedit_value = QLineEdit()
        groupbox1_grid_lineedit_value.setValidator(QDoubleValidator(0.0, 10000.0, 2, notation=QDoubleValidator.StandardNotation))
        groupbox1_grid_lineedit_value.setMaximumWidth(50)
        groupbox1_grid.addWidget(groupbox1_grid_label1, 0, 0)
        groupbox1_grid.addWidget(groupbox1_grid_spinbox1, 0, 1)
        groupbox1_grid.addWidget(groupbox1_grid_label2, 1, 0)
        groupbox1_grid.addWidget(groupbox1_grid_spinbox2, 1, 1)
        groupbox1_grid.addWidget(groupbox1_grid_label3, 2, 0)
        groupbox1_grid.addWidget(groupbox1_grid_lineedit_value, 2, 1)
        groupbox1.setLayout(groupbox1_grid)
        #
        groupbox2_title = "Ограничения смещения пути км/ч"   # продольного/поперечного\n
        groupbox2 = QGroupBox(groupbox2_title, alignment=Qt.AlignHCenter)
        groupbox2.setStyleSheet(groupbox_style)
        groupbox2_hbox = QHBoxLayout()
        groupbox2.setLayout(groupbox2_hbox)
        #
        groupbox2_1_title = "Сдвижка мм"
        groupbox2_1 = QGroupBox(groupbox2_1_title, alignment=Qt.AlignHCenter)
        groupbox2_1.setStyleSheet(groupbox_style)
        groupbox2_1_grid = QGridLayout()
        groupbox2_1_grid_label1 = QLabel("Лево")
        groupbox2_1_grid_label2 = QLabel("Право")
        groupbox2_1_grid_spinbox1 = QSpinBox()
        groupbox2_1_grid_spinbox1.setRange(0, 1000000)
        groupbox2_1_grid_spinbox2 = QSpinBox()
        groupbox2_1_grid_spinbox2.setRange(-1000000000, 0)
        groupbox2_1_grid.addWidget(groupbox2_1_grid_label1, 0, 0)
        groupbox2_1_grid.addWidget(groupbox2_1_grid_spinbox1, 0, 1)
        groupbox2_1_grid.addWidget(groupbox2_1_grid_label2, 1, 0)
        groupbox2_1_grid.addWidget(groupbox2_1_grid_spinbox2, 1, 1)
        groupbox2_1.setLayout(groupbox2_1_grid)
        #
        groupbox2_2_title = "Подъёмка мм"
        groupbox2_2 = QGroupBox(groupbox2_2_title, alignment=Qt.AlignHCenter)
        groupbox2_2.setStyleSheet(groupbox_style)
        groupbox2_2_grid = QGridLayout()
        groupbox2_2_grid_label1 = QLabel("Макс")
        groupbox2_2_grid_label2 = QLabel("Мин")
        groupbox2_2_grid_spinbox1 = QSpinBox()
        groupbox2_2_grid_spinbox1.setRange(0,1000000)
        groupbox2_2_grid_spinbox2 = QSpinBox()
        groupbox2_2_grid_spinbox2.setRange(0, 1000000)
        groupbox2_2_grid.addWidget(groupbox2_2_grid_label1, 0, 0)
        groupbox2_2_grid.addWidget(groupbox2_2_grid_spinbox1, 0, 1)
        groupbox2_2_grid.addWidget(groupbox2_2_grid_label2, 1, 0)
        groupbox2_2_grid.addWidget(groupbox2_2_grid_spinbox2, 1, 1)
        groupbox2_2.setLayout(groupbox2_2_grid)
        #
        # rb = QRadioButton()
        # rb_label = QLabel("Прямая вставка")
        # rb_label.setAlignment(Qt.AlignLeft)
        # rb_hbox = QHBoxLayout()
        # rb_hbox.addWidget(rb)
        # rb_hbox.addWidget(rb_label)
        #
        ok_button = QPushButton("OK")
        ok_button.setMaximumWidth(100)
        #ok_button.setAlignment(Qt.AlignCenter)
        groupbox2_hbox.addWidget(groupbox2_1)
        groupbox2_hbox.addWidget(groupbox2_2)
        #
        info_label = QLabel("Перемещение по меню клавишей 'tab'.\n Изменение параметров стрелками\n либо числовым вводом.")
        info_label.setAlignment(Qt.AlignHCenter)
        info_label.setStyleSheet("border: 2px solid #999999;border-radius: 5px;padding:10px;font-size: 16px;")
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        vbox.addWidget(top_label)
        vbox.addWidget(groupbox1)
        vbox.addWidget(groupbox2)
        vbox.addWidget(ok_button)
        vbox.addWidget(info_label)
        self.setLayout(vbox)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = Main()
    MW.show()
    sys.exit(app.exec())

