import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit
from PySide6.QtTest import QTest

class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        menu = self.menuBar().addMenu('File')
        menu.addAction('Test', self.handleTest, 'Ctrl+N')
        self.edit = QLineEdit(self)
        self.setCentralWidget(self.edit)

    def handleTest(self):
        self.edit.setText('test')

class AppTestCase(unittest.TestCase):
    def setUp(self):
        qApp = QApplication.instance()
        if qApp is None:
            self.app = QApplication([''])
        else:
            self.app = qApp



class WindowTestCase(AppTestCase):
    def setUp(self):
        super(WindowTestCase, self).setUp()
        self.window = Window()
        self.window.show()
        QTest.qWaitForWindowExposed(self.window)

    def test_input_object_in_new_file(self):
        text = 'test'
        self.assertNotEqual(text, self.window.edit.text())
        QTest.keyClicks(self.window, 'n', Qt.ControlModifier)
        self.assertEqual(text, self.window.edit.text())

    def test_enter_text(self):
        text = 'foobar'
        self.assertNotEqual(text, self.window.edit.text())
        QTest.keyClicks(self.window.edit, text)
        self.assertEqual(text, self.window.edit.text())

if __name__ == "__main__":
    unittest.main()