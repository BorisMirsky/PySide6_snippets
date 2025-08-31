import sys
import unittest
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
########################################## Частная переменная #####################################
class Main():
    def __init__(self):
        self.__private_var = 7

class MainTest(unittest.TestCase):
    def setUp(self):
        self.main_instance = Main()

    def test_return_private_var(self):
        test_main_instance = self.main_instance._Main__private_var              # работает
        self.assertEqual(test_main_instance, 7)

#unittest.main()

######################################### Частная переменная Qt ######################################

class QtMain(QWidget):
    def __init__(self, parent: QWidget = None):
        super(QtMain, self).__init__(parent)
        self.resize(300, 200)
        self.__btn = QPushButton('btn')
        vbox = QVBoxLayout()
        vbox.addWidget(self.__btn)
        self.setLayout(vbox)

class QtMainTest(unittest.TestCase):
    def setUp(self):
        self.view = QtMain()

    def test_on_click_button(self):
        #btn = self.view.__btn                      # не работает
        btn = self.view._QtMain__btn                  # не работает
        QTest.mouseClick(btn, Qt.LeftButton)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QtMain()
    #print(dir(window))
    #window.show()
    #sys.exit(app.exec())
    unittest.main()
