import sys, unittest
from PySide6 import QtTest, QtCore, QtQuickTest
#from QtTest import Q
from PySide6.QtWidgets import QApplication
import unittest
from ...main.main import Main
from ...first.buttons import Buttons
from ...second.line_edit import LineEdit



class Test_Main(unittest.TestCase):
    def init(self):
        self.main = Main()
        #self.buttons_class = Buttons()
        self.main.show()
        self.assertEqual(self.main.test_lbl.text(), "MainView")
        self.assertEqual(self.main.btn1.text(), "btn1")
        self.assertEqual(self.main.btn2.text(), "btn2")

    def test_handleBtn1(self):
        self.init()
        QtTest.QTest.mouseClick(self.main.btn1, QtCore.Qt.LeftButton)
        self.assertEqual(id(self.main.layout.currentWidget()), id(self.main.buttons_class))    #id(Buttons()))

    def test_handleBtn2(self):
        self.init()
        QtTest.QTest.mouseClick(self.main.btn2, QtCore.Qt.LeftButton)
        self.assertEqual(id(self.main.layout.currentWidget()), id(self.main.line_edit_class))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    main = Test_Main()
    app.setActiveWindow(main)
    main.show()