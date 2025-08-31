from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import time

"""
Есть 2 кнопки - старт и стоп (+ пауза?).

Отображает
1. Прошедшее время 'hh:mm:ss' (верхний ряд, 2я метка справа)
2. Есть стартовая отметка (где брать старт?!?!) в 'km:m:mm', которая растёт со скоростью 100mm в секунду
   Это три окошка в разделе 'Положение: '
3. Есть такая же отметка, но с 0 (?). Это одно окошко 'Пройдено: '
4. Скорость 100mm в секунду (так?)
5. Сделать одинаковый стиль (цвет и фон)
Нужен класс (функция?), который будет генерить просто таймер (не QTimer), отдающий строковые (timestamp?)
 значения для большого виджета.
 
Запуск таймера с открытием окна (не по кнопке) -> считается (1),(2),(3)    
"""

def func_timer():
    while True:
        a,b,c,d = 0,0,0,0
        sec = 999 + 999*60 + 999*3600 + 999*216000
        for i in range(sec):
            #time.sleep(1)
            a += 1
            result = "{c}:{b}:{a}".format(c = c, b = b, a = a)
            #print(result)
            if a / 60 == 1:
                b += 1
                a = 0
            if b / 60 == 1:
                c += 1
                b = 0

#func_timer()

class ExportTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(100, 30)
        self.initUI()

    def initUI(self):
        self.label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.timer = func_timer()
        self.timer.timeout.connect(self.displayTime)
        self.setLayout(layout)

    def displayTime(self):
        self.label.setText(self.timer_func())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ExportTimer()
    gui.show()
    sys.exit(app.exec())



