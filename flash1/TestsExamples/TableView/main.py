import sys
import pandas as pd
from PySide6.QtCore import QDateTime, QTimeZone
from PySide6.QtWidgets import QApplication

from main_window import MainWindow
from main_widget import MyTableWidget


def read_data(fname):
    df = pd.read_csv(fname)
    a,b,c,d,e,f,k,n = df['Точка'],df['км+м'],df['круговой'],df['переходной'],df['Радиус'],df['левого'],df['правого'],df['уклонОтвода']
    return a,b,c,d,e,f,k,n


if __name__ == "__main__":
    data = read_data('my_data.csv')
    app = QApplication(sys.argv)
    widget = MyTableWidget(data)
    window = MainWindow(widget)
    window.show()
    sys.exit(app.exec())

