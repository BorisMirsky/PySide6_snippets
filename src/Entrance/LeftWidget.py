from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from VerticalLine import VerticalLineModel, MoveLineController
import pandas as pd
import sys


DATAFILE = "example_csv_file.csv"
def read_csv_file(file, n):
    try:
        df = pd.read_csv(file)
        col = df.loc[:, n]
        return col.values.tolist()
    except FileNotFoundError:
        pass


CHARTS_DICT = {1:['plan_mes','plan_prj', 'План'],
               2:['prof_mes','prof_prj', 'Уровень'],
               3:['vozv_mes','vozv_prj', 'Профиль'],
               4:['plan_d'],
               5:['prof_d']}


class MyWidget(QWidget):
    def __init__(self, n, x):
        super().__init__()
        self.x = 20  
        self.resize(150, 100)
        self.n = n
        self.line_edit_1 = QLineEdit()
        self.line_edit_2 = QLineEdit()
        #self.setStyleSheet("background-color: Azure;")   # border-width: 2px;border-color: black;
        self.init_UI()

    def updateX(self, newX):
        if self.n in [1,2,3]:
            data1 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][0])
            data2 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][1])
            chart_name_1_value = data1[newX]
            chart_name_2_value = data2[newX]
            self.line_edit_1.setText(str(chart_name_1_value))
            self.line_edit_2.setText(str(chart_name_2_value))
        else:
            data1 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][0])
            label_name = CHARTS_DICT[self.n][0]
            chart_name_1 = CHARTS_DICT[self.n][0]
            chart_name_1_value = data1[newX]
            self.line_edit_1.setText(str(chart_name_1_value))

        
    def init_UI(self):
        data1, data2 = None, None
        label_name, chart_name_1, chart_name_2,chart_name_1_value,chart_name_2_value = None,None,None,None, None
        if self.n in [1,2,3]:
            data1 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][0])
            data2 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][1])
            chart_name_1 = CHARTS_DICT[self.n][0]
            chart_name_2 = CHARTS_DICT[self.n][1]
            label_name = CHARTS_DICT[self.n][2]
            chart_name_1_value = data1[self.x]
            chart_name_2_value = data2[self.x]
        else:
            data1 = read_csv_file(DATAFILE, CHARTS_DICT[self.n][0])
            label_name = CHARTS_DICT[self.n][0]
            chart_name_1 = CHARTS_DICT[self.n][0]
            chart_name_1_value = data1[self.x]

        layout = QVBoxLayout()

        hbox1 = QHBoxLayout()
        lbl1 = QLabel(label_name, alignment=Qt.AlignmentFlag.AlignHCenter)
        lbl1.setStyleSheet('''font-weight: bold; font-size: 18px;''')
        hbox1.addWidget(lbl1)
        layout.addLayout(hbox1)

        hbox2 = QHBoxLayout()
#        self.line_edit_1 = QLineEdit()
        self.line_edit_1.setStyleSheet('''font-weight: bold; font-size: 14px;''')
        self.line_edit_1.setReadOnly(True)
        self.line_edit_1.setText(str(chart_name_1_value))
        self.line_edit_1.setFixedSize(80, 40)
        lbl2 = QLabel(chart_name_1)
        lbl2.setStyleSheet('''font-weight: bold; font-size: 14px; color: green''')
        hbox2.addWidget(self.line_edit_1)
        hbox2.addWidget(lbl2)
        layout.setSpacing(0)
        layout.addLayout(hbox2)

        if chart_name_2:
            hbox3 = QHBoxLayout()
            self.line_edit_2 = QLineEdit()
            self.line_edit_2.setStyleSheet('''font-weight: bold; font-size: 14px;''')
            self.line_edit_2.setReadOnly(True)
            self.line_edit_2.setText(str(chart_name_2_value))
            self.line_edit_2.setFixedSize(80, 40)
            lbl3 = QLabel(chart_name_2)
            lbl3.setStyleSheet('''font-weight: bold; font-size: 14px; color: red''')
            hbox3.addWidget(self.line_edit_2)
            hbox3.addWidget(lbl3)
            layout.addLayout(hbox3)
        layout.setSpacing(1)
        self.setLayout(layout)



#if __name__ == '__main__':
#    app = QApplication(sys.argv)
#    w = MyWidget(2)   #, 144)
#    w.show()
#    sys.exit(app.exec())
