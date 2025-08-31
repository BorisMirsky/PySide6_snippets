from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QApplication, QHBoxLayout, QGridLayout, QLabel
import sys
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor
from ServiceInfo import DATA_LEN
from Charts import ChartsWidget
from VerticalLine import VerticalLineModel
from Infopanel import InfopanelFirst, InfopanelSecond
from LeftColumnWidget import LeftColumnWidget



class MainWidget(QWidget):
    def __init__(self, v_model:VerticalLineModel):
        super().__init__()
        self.vertical_model = v_model
        grid = QGridLayout()
        infopanel_first = InfopanelFirst()
        infopanel_second = InfopanelSecond()
        grid.addWidget(infopanel_first, 0, 0, 1, 7)
        grid.addWidget(infopanel_second, 1, 0, 1, 7)
        charts_widget = ChartsWidget('plan_prj', 'plan_fact', 'plan_delta',
                      'vozv_fact','vozv_prj','prof_fact',
                      'prof_prj',  'lbound_prof',
                                     "Стрелы изгиба, мм", "Сдвиги, мм", "ВНР, мм",
                                     "Стрелы, мм", "Подъёмки, мм", self.vertical_model)
        grid.addWidget(charts_widget, 2, 1, 7, 1)
        self.rcw = LeftColumnWidget()
        grid.addWidget(self.rcw, 2, 0, 7, 1)
        self.setLayout(grid)

    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        self.rcw.img1 = QLabel(self)
        self.rcw.pixmap1 = QPixmap('')
        if key == Qt.Key_Z:
            self.rcw.pixmap1 = QPixmap('Data/yellow_narrow1')
            self.rcw.img1.setPixmap(self.rcw.pixmap1)
            self.rcw.plan_red = False
            self.rcw.plan_yellow = True
            self.rcw.plan_green = False
        elif key == Qt.Key_X:
            self.rcw.pixmap1 = QPixmap('Data/red_narrow1')
            self.rcw.img1.setPixmap(self.rcw.pixmap1)
            self.rcw.plan_red = True
            self.rcw.plan_yellow = False
            self.rcw.plan_green = False
        elif key == Qt.Key_C:
            self.rcw.pixmap1 = QPixmap('Data/green_narrow1')
            self.rcw.plan_red = False
            self.rcw.plan_yellow = False
            self.rcw.plan_green = True
        self.rcw.img1.setPixmap(self.rcw.pixmap1)
            #self.plan_yellow = False
            #print('Key_C ')
        #if key == Qt.Key_V:
            #print('Key_V ')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    MW = MainWidget(VerticalLineModel(DATA_LEN * 0.5))
    MW.show()
    sys.exit(app.exec())

