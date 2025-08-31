from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, SIGNAL
from PySide6.QtTest import QTest, QSignalSpy
import sys
import unittest


class Main(QWidget):
    my_signal = Signal(int)
    def __init__(self, parent: QWidget = None):
        super(Main, self).__init__(parent)
        self.resize(300, 200)
        self.counter = 0
        self.lbl = QLabel()
        self.lbl.setNum(self.counter)
        self.btn = QPushButton('btn')
        self.btn.clicked.connect(self.handle_button)
        #self.my_signal.connect(self.func())
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        vbox.addWidget(self.lbl)
        self.setLayout(vbox)

    def handle_button(self):
        self.counter += 1
        self.my_signal.emit(self.counter)

    #def func(self):
    #    self.lbl.setNum(self.counter)

##############################################################
class MainTest(unittest.TestCase):
    def setUp(self):
        self.view = Main()

    def test_on_click_button(self):
        btn = self.view.btn
        QTest.mouseClick(btn, Qt.LeftButton)

    def test_spy_signal(self):
        spy = QSignalSpy(self.view.btn, self.view.my_signal.connect)
        self.assertTrue(spy.isValid())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = Main()
    #window.show()
    #sys.exit(app.exec())
    unittest.main()