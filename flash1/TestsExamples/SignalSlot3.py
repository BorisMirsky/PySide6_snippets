import sys
from PySide6.QtCharts import QCandlestickSeries, QChart, QChartView, QCandlestickSet, QLineSeries
from PySide6.QtWidgets import * #QApplication, QMainWindow, QWidget,QPushButton,QSpinBox,QDialog,QDial,QHBoxLayout
from PySide6.QtCore import Qt, QPointF, QObject, QTimer # pyqtSignal
from PySide6.QtCore import Signal, Slot

from collections import OrderedDict
from time import sleep

class Analyst(QObject):

    finished = Signal((object,), (list,))

    def __init__(self, parent=None):
        super(Analyst, self).__init__(parent=parent)

        self.number = 10000.0

    def analyze(self):
        print("Analyst working!")
        result = OrderedDict()
        result["a"] = self.number / 100.0
        result["b"] = self.number / 200.0

        sleep(1)

        report = ['Analysis Report',
                  ' a: {0}'.format(result["a"]),
                  ' b: {0}'.format(result["b"])
                  ]

        print("Analyst done!")

        self.finished[object].emit(result)
        sleep(1)
        self.finished[list].emit(report)

class Manager(QObject):

    announceStartWork = Signal()
    allDone = Signal()

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent=parent)

        self.analyst = Analyst(self)
        self.analyst.finished[object].connect(self.post_process)
        self.analyst.finished[list].connect(self.report_result)
        self.announceStartWork.connect(self.analyst.analyze)
        self.reportsDone = False
        self.resultsDone = False
        self.allDone.connect(self.exitWhenReady)

    def directAnalyst(self):
        print("Telling analyst to start")
        self.announceStartWork.emit()

    def post_process(self, results):
        print("Results type (expecting OrderedDict): {0}".format(type(results)))
        if issubclass(type(results), dict):
            summation = 0
            for value in results.values():
                summation += value

            print("Sum of Results: {0}".format(summation))
            self.resultsDone = True
            self.allDone.emit()
        else:
            print("*** WRONG TYPE! DICT slot got the LIST!")


    def report_result(self, report):

        print("Report type (expecting list): {0}".format(type(report)))

        if issubclass(type(report), list):
            report_str = '\n'.join(report)
            print("Report of original result: \n{0}".format(report_str))

            self.reportsDone = True
            self.allDone.emit()
        else:
            print("*** WRONG TYPE! LIST slot got the DICT!")


    def exitWhenReady(self):
        tasksCompleted = [self.reportsDone, self.resultsDone]
        if all(tasksCompleted):
            print("All tasks completed")
            app.exit()
        else:
            print("Not all tasks completed yet")


if __name__ == "__main__":
    app = QApplication([])
    manager = Manager()
    manager.directAnalyst()
    sys.exit(app.exec())