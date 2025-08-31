import sys

from PySide6.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QApplication, QGridLayout, QMainWindow, QComboBox, QFrame, QMenuBar, QStatusBar, QWidget
from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.year_ccb = QComboBox(self.centralwidget)
        self.year_ccb.setGeometry(QRect(10, 10, 111, 22))
        self.year_ccb.setObjectName("year_ccb")
        self.chart_fm = QFrame(self.centralwidget)
        self.chart_fm.setGeometry(QRect(20, 60, 741, 391))
        self.chart_fm.setFrameShape(QFrame.StyledPanel)
        self.chart_fm.setFrameShadow(QFrame.Raised)
        self.chart_fm.setObjectName("chart_fm")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


class LoginWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.build_chart()

        years = ("2019", "2020", "2021")
        self.ui.year_ccb.currentIndexChanged.connect(self.handle_index_changed)
        self.ui.year_ccb.addItems(years)

    def build_chart(self):
        self.series = QBarSeries()
        self.set_tkf = QBarSet("TAEKWON-DO")
        self.set_fenc = QBarSet("ΞΙΦΑΣΚΙΑ")
        self.set_oplo = QBarSet("ΟΠΛΟΜΑΧΙΑ")
        self.set_spends = QBarSet("ΕΞΟΔΑ")
        self.series.append(self.set_tkf)
        self.series.append(self.set_fenc)
        self.series.append(self.set_oplo)
        self.series.append(self.set_spends)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Monthly Stats per Year")
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chart.setTheme(QChart.ChartThemeBrownSand)
        self.chart.setBackgroundBrush(QBrush(QColor("transparent")))
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.axisX = QBarCategoryAxis()
        self.axisY = QValueAxis()
        self.axisY.setRange(0, 3000)

        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        self.chartview = QChartView(self.chart)
        vbox = QGridLayout(self.ui.chart_fm)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.chartview)

    def handle_index_changed(self):
        default = [
            ["10", "11", "12", "13", "14"],
            [
                (45, 67, 12, 43),
                (127, 54, 132, 454),
                (435, 187, 212, 453),
                (45, 657, 152, 455),
                (45, 667, 122, 475),
            ],
        ]
        data = {
            "2019": [
                ["1", "2", "3", "4", "5"],
                [
                    (45, 637, 12, 43),
                    (12, 154, 132, 454),
                    (435, 117, 212, 453),
                    (45, 657, 112, 455),
                    (451, 667, 12, 475),
                ],
            ],
            "2020": [
                ["5", "6", "7", "8", "9"],
                [
                    (425, 67, 172, 43),
                    (192, 584, 132, 454),
                    (435, 167, 212, 453),
                    (45, 657, 12, 455),
                    (453, 667, 162, 475),
                ],
            ],
        }
        values = data.get(self.ui.year_ccb.currentText(), default)
        self.update_chart_one(values)

    def update_chart_one(self, datas):
        self.axisX.clear()
        self.set_tkf.remove(0, self.set_tkf.count())
        self.set_fenc.remove(0, self.set_fenc.count())
        self.set_oplo.remove(0, self.set_oplo.count())
        self.set_spends.remove(0, self.set_spends.count())
        categories, data = datas
        self.axisX.append(categories)
        for tkf, fenc, oplo, spends in data:
            self.set_tkf.append(tkf)
            self.set_fenc.append(fenc)
            self.set_oplo.append(oplo)
            self.set_spends.append(spends)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())