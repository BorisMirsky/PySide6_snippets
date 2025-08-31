from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, SIGNAL
from PySide6.QtTest import QTest, QSignalSpy
import sys
import unittest


class Main(QWidget):
    mySignal = Signal(int)
    def __init__(self, parent: QWidget = None):
        super(Main, self).__init__(parent)
        self.resize(300, 200)
        self.counter = 0
        self.lbl = QLabel()
        self.lbl.setNum(self.counter)
        self.btn = QPushButton('btn')
        self.btn.clicked.connect(self.handle_button)
        self.mySignal.connect(self.checkHonest)
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn)
        vbox.addWidget(self.lbl)
        self.setLayout(vbox)

    def handle_button(self):
        self.counter += 1
        self.lbl.setNum(self.counter)
        if self.counter % 2 == 0:
            self.mySignal.emit(self.counter)

    def checkHonest(self, c:int):
        print(c, 'honest')

##############################################################
class MainTest(unittest.TestCase):
    def setUp(self):
        self.view = Main()

    def test_on_click_button(self):
        btn = self.view.btn
        QTest.mouseClick(btn, Qt.LeftButton)

    #QSignalSpy - только в PySide, не PyQt!
    def test_spy_signal(self):
      spy = QSignalSpy(self.view.btn, Signal(clicked(int)))
      self.assertTrue(spy.isValid())
      self.assertEqual(len(spy), 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())
    #unittest.main()