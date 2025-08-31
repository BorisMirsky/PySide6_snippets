import time
from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys



"""
Надо привязать скорость машины к скорости времени.
Для этого нужен счетчик.
В спин-боксе выставляется скорость. Диапазон от 1см\сек до 20 см\сек.
Затем эта скорость отдаётся в 4 окошка:
1 Счётчик - т.е. пройденное время
  Уже написан.
  Верхняя панель справа, рядом с счетчиком реального времени.

               Второй ряд окошек
2 Скорость - в км\ч, статичная
  Получаем готовую и только пересчитать см\сек в км\ч
3 Пройдено - в метрах
  Счётчик, считает в метрах float , пересчёт из скорости
  Скорость (2) * время (1)
4 Положение - стартовая метка плюс пройдено
  Прибавляем к const найденный (3)
Лучше это отдельным классом (или в этом же ещё методы написать?)
Принимать он будет из написанного счётчика.

Спин-бокс установки скорости рядом с кнопками старт и стоп.

Кнопка пауза нужна?
"""

class Window(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Stop watch")
        self.setGeometry(100, 100, 400, 500)
        self.UiComponents()
        self.show()
 
    def UiComponents(self):
        self.count = 0
        self.flag = False
        self.label = QLabel(self)
        self.label.setGeometry(75, 100, 250, 70)
        self.label.setStyleSheet("border : 4px solid black;")
        self.label.setText(str(self.count))
        self.label.setFont(QFont('Arial', 25))
        self.label.setAlignment(Qt.AlignCenter)
        start = QPushButton("Start", self)
        start.setGeometry(125, 250, 150, 40)
        start.pressed.connect(self.Start)
        pause = QPushButton("Pause", self)
        pause.setGeometry(125, 300, 150, 40)
        pause.pressed.connect(self.Pause)
        re_set = QPushButton("Re-set", self)
        re_set.setGeometry(125, 350, 150, 40)
        re_set.pressed.connect(self.Re_set)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

    def showTime(self):
        if self.flag:
            self.count+= 1
        text = str(self.count) # / 10)
        self.label.setText(text)
        #print(text)
 
    def Start(self):
        self.flag = True
 
    def Pause(self):
        self.flag = False
 
    def Re_set(self):
        self.flag = False
        self.count = 0
        self.label.setText(str(self.count))


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
