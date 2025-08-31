
import sys
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
import MargaritaMixer

#app = QApplication(sys.argv)

class MargaritaMixerTest(unittest.TestCase):
    def setUp(self):
        self.form = MargaritaMixer.MargaritaMixer()

    def setFormToZero(self):
        self.form.ui.tequilaScrollBar.setValue(0)
        self.form.ui.tripleSecSpinBox.setValue(0)
        self.form.ui.limeJuiceLineEdit.setText("0.0")
        self.form.ui.iceHorizontalSlider.setValue(0)

    def test_defaults(self):
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 8)
        self.assertEqual(self.form.ui.tripleSecSpinBox.value(), 4)
        self.assertEqual(self.form.ui.limeJuiceLineEdit.text(), "12.0")
        self.assertEqual(self.form.ui.iceHorizontalSlider.value(), 12)
        self.assertEqual(self.form.ui.speedButtonGroup.checkedButton().text(), "&Karate Chop")
        self.assertEqual(self.form.jiggers, 36.0)
        self.assertEqual(self.form.speedName, "&Karate Chop")
        #okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        btn_ok = self.form.ui.btn_ok
        btn_cancel = self.form.ui.btn_cancel
        QTest.mouseClick(btn_ok, Qt.LeftButton)
        QTest.mouseClick(btn_cancel, Qt.LeftButton)
        #QTest.mouseClick(okWidget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 36.0)
        self.assertEqual(self.form.speedName, "&Karate Chop")
        

    def test_tequilaScrollBar(self):
        self.setFormToZero()
        self.form.ui.tequilaScrollBar.setValue(12)
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 12)
        self.form.ui.tequilaScrollBar.setValue(-1)
        self.assertEqual(self.form.ui.tequilaScrollBar.value(), 0)
        self.form.ui.tequilaScrollBar.setValue(5)
        btn_ok = self.form.ui.btn_ok
        btn_cancel = self.form.ui.btn_cancel
        QTest.mouseClick(btn_ok, Qt.LeftButton)
        #QTest.mouseClick(btn_cancel, Qt.LeftButton)
        #okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        #QTest.mouseClick(okWidget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 5)

    def test_tripleSecSpinBox(self):
        self.setFormToZero()
        self.form.ui.tripleSecSpinBox.setValue(2)
        btn_ok = self.form.ui.btn_ok
        btn_cancel = self.form.ui.btn_cancel
        QTest.mouseClick(btn_ok, Qt.LeftButton)
        # QTest.mouseClick(btn_cancel, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 2)

    def test_limeJuiceLineEdit(self):
        self.setFormToZero()
        self.form.ui.limeJuiceLineEdit.clear()
        QTest.keyClicks(self.form.ui.limeJuiceLineEdit, "3.5")
        btn_ok = self.form.ui.btn_ok
        btn_cancel = self.form.ui.btn_cancel
        QTest.mouseClick(btn_ok, Qt.LeftButton)
        # QTest.mouseClick(btn_cancel, Qt.LeftButton)
        #okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
        #QTest.mouseClick(okWidget, Qt.LeftButton)
        self.assertEqual(self.form.jiggers, 3.5)

    # def test_iceHorizontalSlider(self):
    #     self.setFormToZero()
    #     self.form.ui.iceHorizontalSlider.setValue(4)
    #     okWidget = self.form.ui.buttonBox.button(self.form.ui.buttonBox.Ok)
    #     QTest.mouseClick(okWidget, Qt.LeftButton)
    #     self.assertEqual(self.form.jiggers, 4)
    #
    # def test_liters(self):
    #     self.setFormToZero()
    #     self.assertAlmostEqual(self.form.liters, 0.0)
    #     self.form.ui.iceHorizontalSlider.setValue(1)
    #     self.assertAlmostEqual(self.form.liters, 0.0444)
    #     self.form.ui.iceHorizontalSlider.setValue(2)
    #     self.assertAlmostEqual(self.form.liters, 0.0444 * 2)
    #
    # def test_blenderSpeedButtons(self):
    #     self.form.ui.speedButton1.click()
    #     self.assertEqual(self.form.speedName, "&Mix")
    #     self.form.ui.speedButton2.click()
    #     self.assertEqual(self.form.speedName, "&Whip")
    #     self.form.ui.speedButton3.click()
    #     self.assertEqual(self.form.speedName, "&Puree")
    #     self.form.ui.speedButton4.click()
    #     self.assertEqual(self.form.speedName, "&Chop")
    #     self.form.ui.speedButton5.click()
    #     self.assertEqual(self.form.speedName, "&Karate Chop")
    #     self.form.ui.speedButton6.click()
    #     self.assertEqual(self.form.speedName, "&Beat")
    #     self.form.ui.speedButton7.click()
    #     self.assertEqual(self.form.speedName, "&Smash")
    #     self.form.ui.speedButton8.click()
    #     self.assertEqual(self.form.speedName, "&Liquefy")
    #     self.form.ui.speedButton9.click()
    #     self.assertEqual(self.form.speedName, "&Vaporize")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
