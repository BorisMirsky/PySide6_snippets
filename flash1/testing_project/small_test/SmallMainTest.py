import sys, unittest
from PySide6 import QtTest, QtCore
from PySide6.QtWidgets import QApplication
from .SmallMain import MyWidget



class WidgetTest(unittest.TestCase):
    def init(self):
        self.form = MyWidget()
        self.form.show()
        self.assertEqual(self.form.cmb.currentText(), "A")
        self.assertEqual(self.form.lbl.text(), "default")

    def test_button(self):
        self.init()
        QtTest.QTest.mouseClick(self.form.but, QtCore.Qt.LeftButton)
        self.assertEqual(self.form.cmb.currentText(), "A")
        self.assertEqual(self.form.lbl.text(), "A 1")

    def test_combobox(self):
        self.init()
        QtTest.QTest.keyClick(self.form.cmb, QtCore.Qt.Key_PageDown)
        QtTest.QTest.qWait(100)
        self.assertEqual(self.form.cmb.currentText(), "B")
        self.assertEqual(self.form.lbl.text(), "B 0")

    def test_visibility(self):
        self.init()
        self.assertEqual(self.form.isVisible(), True)
        self.assertEqual(self.form.cmb.isVisible(), True)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    mainw = WidgetTest()
    app.setActiveWindow(mainw)
    mainw.show()