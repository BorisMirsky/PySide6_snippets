from PySide6.QtWidgets import *
#from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtCharts import *
from ScrolledChart import ChartClass, ScrollChartClass
from VerticalLine import VerticalLineModel, MoveLineController
import pandas as pd
from LeftWidget import MyWidget


DATAFILE = "example_csv_file.csv"

DATAFILE_LEN = len(pd.read_csv(DATAFILE))



# обработка случая 'отказ от выбора файла'
def read_csv_file( file, n):
    try:
        df = pd.read_csv(file)
        col = df.loc[:, n]
        return col.values.tolist()
    except FileNotFoundError:
        pass

pos=20

class Main(QWidget):
    def __init__(self, model, parent: QObject = None):
        super().__init__(parent)
        self.leftWidget1 = MyWidget(1, pos)
        self.leftWidget2 = MyWidget(2, pos) 
        self.leftWidget3 = MyWidget(3, pos) 
        self.leftWidget4 = MyWidget(4, pos) 
        self.leftWidget5 = MyWidget(5, pos) 
        self.model = VerticalLineModel()
        self.model.positionChanged.connect(self.updateCurrentPositionInfo)
        self.createLeftBottomWidget()
        self.initUI()


    def updateCurrentPositionInfo(self, position):
        self.leftWidget1.updateX(position)
        self.leftWidget2.updateX(position)
        self.leftWidget3.updateX(position)
        self.leftWidget4.updateX(position)
        self.leftWidget5.updateX(position)


    def initUI(self):
        chart1 = ChartClass(DATAFILE, 1)        
        scroll1 = ScrollChartClass(chart1)     
        chart2 = ChartClass(DATAFILE, 2)  
        scroll2 = ScrollChartClass(chart2)     
        chart3 = ChartClass(DATAFILE, 3)
        scroll3 = ScrollChartClass(chart3)
        chart4 = ChartClass(DATAFILE, 4)
        scroll4 = ScrollChartClass(chart4)
        chart5 = ChartClass(DATAFILE, 5)
        scroll5 = ScrollChartClass(chart5)

        GridLayout = QGridLayout()
        GridLayout.addWidget(self.leftWidget1, 0, 0)
        GridLayout.addWidget(self.leftWidget2, 1, 0)
        GridLayout.addWidget(self.leftWidget3, 2, 0)
        GridLayout.addWidget(self.leftWidget4, 3, 0)
        GridLayout.addWidget(self.leftWidget5, 4, 0)
        GridLayout.addWidget(self.leftBottomWidget, 5, 0)
        GridLayout.addWidget(scroll1, 0, 1)
        GridLayout.addWidget(scroll2, 1, 1)
        GridLayout.addWidget(scroll3, 2, 1)
        GridLayout.addWidget(scroll4, 3, 1)
        GridLayout.addWidget(scroll5, 4, 1)
        GridLayout.setSpacing(5)
        GridLayout.setColumnStretch(1, 4)
        self.lineMover = MoveLineController(self.model)
        self.installEventFilter(self.lineMover)
        self.setLayout(GridLayout)

    def createLeftBottomWidget(self):
        leftBottomLayout = QVBoxLayout()
        leftBottomLayout.addStretch(1)
        hbox = QVBoxLayout()
        lbl_name = QLabel('Переместиться\n на координату')
        lbl_name.setStyleSheet('''font-weight: bold; font-size: 15px;''')
        hbox.addWidget(lbl_name)
        self.line = QSpinBox()
        self.line.setRange(0, DATAFILE_LEN)
        #self.line = QLineEdit()
        #self.line.setValidator(QDoubleValidator(0, 17, 1, self))
        # self.line.textChanged[str].connect(self.getInputNewCoord)
        self.line.valueChanged.connect(self.spinBoxHandling)
        #self.line.textChanged[str].connect(self.updateCurrentPositionInfo) #getInputNewCoord)
        self.line.setFixedWidth(70)
        hbox.addWidget(self.line)
        leftBottomLayout.addLayout(hbox)
        self.leftBottomWidget = QWidget()
        self.leftBottomWidget.setLayout(leftBottomLayout)

    def spinBoxHandling(self):
        value = self.line.value()
        #valueChanged = Signal(int)
        #self.valueChanged.emit(self.__currentX)
        print(value)



if __name__ == "__main__":
    import sys
    app = QApplication()
    model = VerticalLineModel()
    w = Main(model)
    w.show()
    sys.exit(app.exec())
