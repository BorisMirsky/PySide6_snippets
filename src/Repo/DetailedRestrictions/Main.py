from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout, QApplication, QHBoxLayout, QGridLayout
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, Qt, QPen,QColor
from PySide6.QtCore import Qt, QObject, QCoreApplication, Signal
import sys
from ServiceInfo import DATA_LEN
from Charts import Chart1, Chart2   #ChartsWidget
from VerticalLine import VerticalLineModel1
from HorizontalLine import HorizontalLineModel



class MainWidget(QWidget):
    def __init__(self, v_model:VerticalLineModel1):
        super().__init__()
        self.vertical_model = v_model
        grid = QGridLayout()
        self.chart1 = Chart1('plan_prj', 'plan_fact', self.vertical_model)
        chart2 = Chart2('plan_delta', self.vertical_model)
        grid.addWidget(self.chart1, 0, 0, 5, 9)
        grid.addWidget(chart2, 5, 0, 3, 9)
        rcw = self.rightColumnWidget()
        grid.addLayout(rcw, 1, 9, 1, 1)   
        self.setLayout(grid)
        self.setFocus()

    def rightColumnWidget(self):    
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        widget = QWidget()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        label_name = QLabel("План")
        label_name.setStyleSheet("font:bold; font-size:16pt;") # color:white;background-color:black")
        hbox1.addWidget(label_name)
        label_prj_name = QLabel("Проект")
        label_prj_name.setStyleSheet("font:bold; font-size:13pt; color:red;") #background-color:black")
        label_prj_value = QLabel()
        label_prj_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        hbox2.addWidget(label_prj_name)
        hbox2.addWidget(label_prj_value)
        label_fact_name = QLabel("Натура")
        label_fact_name.setStyleSheet("font:bold; font-size:13pt; color:green;")
        label_fact_value = QLabel()
        label_fact_value.setStyleSheet("font:bold; font-size:13pt; color:yellow; background-color:blue")
        hbox2.addWidget(label_fact_name)
        hbox2.addWidget(label_fact_value)
        self.checkBox_prj = QCheckBox() #"Проект")
        self.checkBox_prj.setChecked(True)
        self.checkBox_prj.stateChanged.connect(self.handleCheckBoxPrj)
        self.checkBox_fact = QCheckBox() #"Натура")
        self.checkBox_fact.setChecked(True)
        self.checkBox_fact.stateChanged.connect(self.handleCheckBoxFact)
        hbox3.addWidget(self.checkBox_prj)
        hbox3.addWidget(self.checkBox_fact)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        return vbox
        #self.setLayout(vbox)


    def handleCheckBoxPrj(self, checked):
        if checked:
            self.chart1.series2.show()
        else:
            self.chart1.series2.hide()
        self.show()
 
    def handleCheckBoxFact(self, checked):
        if checked:
            self.chart1.series1.show()
        else:
            self.chart1.series1.hide() 
        self.show()



#if __name__ == '__main__':
app = QApplication(sys.argv)
MW = MainWidget(VerticalLineModel1(DATA_LEN * 0.5))
MW.show()
sys.exit(app.exec())

