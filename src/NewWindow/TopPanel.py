from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
from QTimerClass import ExportCurrentTime

"""
Функция регулировки скорости.
В текущем примере выставлена скорость 0.01 метра в секунду ->
->  проходимая дистанция отображается в окнах 'км', 'м', 'мм', 'пройдено'.

Функция должна принимать: 
- стартовая отметка на дистанции; 
- настройка (управляет скоростью).

Добавить вертикальные черты

Кнопки 'старт' & 'стоп'
"""

PEREGON = "БРЯНСК-ЛЬГОВСКИЙ - СИНЕЗЕРКИ"
PUT = "1"


def current_time():
    current_time = QDateTime.currentDateTime()
    formatted_time = current_time.toString('hh:mm:ss')
    return formatted_time
    # self.label.setText(formatted_time)

#def counter(distance_lable, setting):




class TopPanelClass(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 100)
        self.init_UI()

    def init_UI(self):
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        label_1_1 = QLabel("Перегон")
        line_edit_1_1 = QLineEdit()
        line_edit_1_1.setText(PEREGON)
        line_edit_1_1.setStyleSheet('''font-weight: bold; font-size: 14px;''')
        line_edit_1_1.setReadOnly(True)
        line_edit_1_1.setFixedSize(500, 30)
        #
        label_1_2 = QLabel("Путь")
        line_edit_1_2 = QLineEdit()
        line_edit_1_2.setText(PUT)
        line_edit_1_2.setStyleSheet('''font-weight: bold; font-size: 14px;''')
        line_edit_1_2.setReadOnly(True)
        line_edit_1_2.setFixedSize(30, 30)
        #
        line_edit_1_3 = QLineEdit()
        line_edit_1_3.setText("ПО пикетажу")
        line_edit_1_3.setStyleSheet('''font-weight: bold; font-size: 14px;''')
        line_edit_1_3.setReadOnly(True)
        line_edit_1_3.setFixedSize(120, 30)
        #
        line_edit_1_4 = QLineEdit()
        line_edit_1_4.setStyleSheet('''font-weight: bold; font-size: 14px;''')
        line_edit_1_4.setReadOnly(True)
        line_edit_1_4.setFixedSize(200, 30)
        line_edit_1_4.setText('Тут будет счётчик')
        #
        hbox1.addWidget(label_1_1)
        hbox1.addWidget(line_edit_1_1)
        hbox1.addWidget(label_1_2)
        hbox1.addWidget(line_edit_1_2)
        hbox1.addWidget(line_edit_1_3)
        hbox1.addWidget(line_edit_1_4)
        current_timer = ExportCurrentTime()
        current_timer.setStyleSheet('''font-weight: bold; font-size: 16px;''')
        hbox1.addWidget(current_timer)
        #
        hbox2 = QHBoxLayout()
        label_2_1 = QLabel("Положение")
        line_edit_2_1 = QLineEdit()
        label_2_2 = QLabel("км+")
        line_edit_2_2 = QLineEdit()
        label_2_3 = QLabel("м+")
        line_edit_2_3 = QLineEdit()
        label_2_4 = QLabel("мм")
        label_2_5 = QLabel("Пройдено")
        line_edit_2_4 = QLineEdit()
        label_2_6 = QLabel("м")
        label_2_7 = QLabel("Скорость")
        line_edit_2_5 = QLineEdit()
        label_2_8 = QLabel("км/ч")
        hbox2.addWidget(label_2_1)
        hbox2.addWidget(line_edit_2_1)
        hbox2.addWidget(label_2_2)
        hbox2.addWidget(line_edit_2_2)
        hbox2.addWidget(label_2_3)
        hbox2.addWidget(line_edit_2_3)
        hbox2.addWidget(label_2_4)
        hbox2.addWidget(label_2_5)
        hbox2.addWidget(line_edit_2_4)
        hbox2.addWidget(label_2_6)
        hbox2.addWidget(label_2_7)
        hbox2.addWidget(line_edit_2_5)
        hbox2.addWidget(label_2_8)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)
        return



if __name__ == '__main__':
   app = QApplication(sys.argv)
   w = TopPanelClass()
   w.show()
   sys.exit(app.exec())