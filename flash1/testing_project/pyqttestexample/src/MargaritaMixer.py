
import sys
from PySide6 import QtGui, QtCore, QtWidgets

from Ui_MargaritaMixer import Ui_MargaritaMixer

class MargaritaMixer(QtWidgets.QWidget):
    def __init__(self):
        super(MargaritaMixer, self).__init__()
        self.ui = Ui_MargaritaMixer()
        self.ui.setupUi(self)
        
    @property
    def jiggers(self):
        jiggersTequila = self.ui.tequilaScrollBar.value()
        jiggersTripleSec = self.ui.tripleSecSpinBox.value()
        jiggersLimeJuice = float(self.ui.limeJuiceLineEdit.text())
        jiggersIce = self.ui.iceHorizontalSlider.value()
        return jiggersTequila + jiggersTripleSec + jiggersLimeJuice + jiggersIce
    
    @property
    def liters(self):
        return 0.0444 * self.jiggers
        
    @property
    def speedName(self):
        speedButton = self.ui.speedButtonGroup.checkedButton()
        if speedButton is None:
            return None
        return speedButton.text()

    def accept(self):
        print('The volume of drinks is {0} liters ({1} jiggers).'.format(self.liters, self.jiggers))
        print('The blender is running at speed "{0}"'.format(self.speedName))
        #self.close()

    def reject(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MargaritaMixer()
    myapp.show()
    sys.exit(app.exec())
