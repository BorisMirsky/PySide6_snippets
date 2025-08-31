import sys, unittest
from PySide6 import QtTest, QtCore, QtQuickTest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, Qt
import unittest
from ...main.main import Main
from ...second.line_edit import LineEdit




class Test_LineEdit(unittest.TestCase):
    def init(self):
        self.lineEdit = LineEdit()
        self.lineEdit.show()
        #self.assertEqual(self.buttons.lbl.text(), '0')

    def test_lineedit(self):
        self.init()
        QtTest.QTest.keyPress(self.lineEdit.le, Qt.Key.Key_Enter)
        if self.lineEdit.lbl.text():
            self.assertEqual(self.lineEdit.lbl.text(), str(int(self.lineEdit.le.text()) ** 2))
        else:
            pass
        #self.assertEqual(self.buttons.counter,1)
    #
    # def test_main_btn_down(self):
    #     self.init()
    #     QtTest.QTest.mouseClick(self.buttons.btn_down, QtCore.Qt.LeftButton)
    #     self.assertEqual(self.buttons.btn_down.text(), "down")
    #     self.assertEqual(self.buttons.counter, -1)
    #
    # def test_goBack(self):
    #     self.init()
    #     spy = QtTest.QSignalSpy(self.buttons.backSignal)
    #     self.main = Main()
    #     self.main.backMain()
        #
        #self.main.currentView = self.main.mainWidget
        #self.main.layout.setCurrentWidget(self.main.currentView)







if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    test_line_edit = Test_LineEdit()
    app.setActiveWindow(test_line_edit)
    test_buttons.show()