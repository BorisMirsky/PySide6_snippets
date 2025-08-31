import sys
from PySide6.QtWidgets import QWidget, QLabel,QVBoxLayout, QApplication, QHBoxLayout, QPushButton, QStackedWidget
from PySide6.QtGui import Qt
from PySide6.QtCore import Qt, QTimer, QCoreApplication, Signal, QTimer, Slot


widget_style = """
    border-style: outset;
    border-width: 2px;
    border-radius: 10px;
    font: 14px;
"""


class StackedExample(QWidget):
    def __init__(self, timer: QTimer(qApp), n:int):
        super(StackedExample, self).__init__()
        self.insertionTimer = timer

        self.time_counter = 1
        self.insertionTimer.timeout.connect(self.set_time)
        self.time_label = QLabel(str(self.time_counter))
        self.insertionTimer.start(n)

        w1 = QWidget()
        w1.setStyleSheet(widget_style)
        w1_layout = QHBoxLayout()
        w1.setLayout(w1_layout)
        lbl1 = QLabel('widget 1')
        w1_layout.addWidget(lbl1)
        w1_layout.addWidget(self.time_label)

        w2 = QWidget()
        w2.setStyleSheet(widget_style)
        w2_layout = QHBoxLayout()
        w2.setLayout(w2_layout)
        lbl2 = QLabel('widget 2')
        w2_layout.addWidget(lbl2)
        w2_layout.addWidget(self.time_label)

        w3 = QWidget()
        w3.setStyleSheet(widget_style)
        w3_layout = QHBoxLayout()
        w3.setLayout(w3_layout)
        lbl3 = QLabel('widget 3')
        w3_layout.addWidget(lbl3)
        w3_layout.addWidget(self.time_label)




        self.Stack = QStackedWidget(self)
        self.Stack.addWidget(w1)
        self.Stack.addWidget(w2)
        self.Stack.addWidget(w3)

        self.stack_counter = 0
        hbox = QHBoxLayout()
        btn = QPushButton('go')
        btn.clicked.connect(self.display)
        hbox.addWidget(self.time_label, 2)
        hbox.addWidget(btn, 1)
        hbox.addWidget(self.Stack, 2)
        self.setLayout(hbox)


    def display(self):
        if 0 <= self.stack_counter < 3:
            self.Stack.setCurrentIndex(self.stack_counter)
            self.stack_counter += 1
        else:
            self.stack_counter = 0

    def set_time(self):
        self.time_counter += 1
        self.time_label.setText(str(self.time_counter))
        #print(self.time_counter)



if __name__ == '__main__':
    insertionTimer = QTimer(qApp)
    app = QApplication(sys.argv)
    ex = StackedExample(insertionTimer, 1000)
    ex.show()
    sys.exit(app.exec())

