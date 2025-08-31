import sys, unittest
from PySide6 import QtTest, QtCore, QtQuickTest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal
import unittest
from ...main.main import Main
from ...first.buttons import Buttons




class Test_Buttons(unittest.TestCase):
    def init(self):
        #self. = Main()
        self.buttons = Buttons()
        self.buttons.show()
        self.assertEqual(self.buttons.lbl.text(), '0')

    def test_main_btn_up(self):
        self.init()
        QtTest.QTest.mouseClick(self.buttons.btn_up, QtCore.Qt.LeftButton)
        self.assertEqual(self.buttons.btn_up.text(), "up")
        self.assertEqual(self.buttons.counter,1)

    def test_main_btn_down(self):
        self.init()
        QtTest.QTest.mouseClick(self.buttons.btn_down, QtCore.Qt.LeftButton)
        self.assertEqual(self.buttons.btn_down.text(), "down")
        self.assertEqual(self.buttons.counter, -1)

    def test_goBack(self):
        self.init()
        spy = QtTest.QSignalSpy(self.buttons.backSignal)
        self.main = Main()
        self.main.backMain()
        #
        #self.main.currentView = self.main.mainWidget
        #self.main.layout.setCurrentWidget(self.main.currentView)







if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    test_buttons = Test_Buttons()
    app.setActiveWindow(test_buttons)
    test_buttons.show()