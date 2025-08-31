
#from ..slider import LabeledSlider
#from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
#from domain.units.MemoryBufferUnit import MemoryBufferUnit
#from operating.states.lining.ApplicationLiningState import LiningProcessState
from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QWidget, QVBoxLayout, QLabel, QApplication,QSlider,QStyleOptionSlider,QStyle
from PySide6.QtGui import QColor,QPainter, QFocusEvent
from PySide6.QtCore import Qt, QPoint, QRect
from typing import Optional
import sys


bottom_label_style = """ border :1px solid; border-color: black; font: 13px; padding: 2px 2px 2px 2px;"""

slider_style_string = """
            QSlider::handle:vertical {
                height: 10px;
                width: 10px;
                background-color: #C0392B;
                }
            QSlider::groove:vertical {
                background: #F4D03F;
            }
    """


class LabeledSlider(QSlider):
    def __init__(self, minimum: int, maximum:int,  value:int, interval=10, parent=None):
        super(LabeledSlider, self).__init__(parent)
        levels=range(minimum, maximum+interval, interval)   #range(minimum, maximum+interval, interval)
        self.value = value
        self.setContentsMargins(20,20,20,20)
        self.levels=list(zip(levels, map(str, levels)))
        self.left_margin, self.top_margin, self.right_margin, self.bottom_margin = 20, 20, 20, 20
        self.orientation = Qt.Vertical
        self.setEnabled(True)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setTickPosition(QSlider.TicksRight)
        self.setMinimumHeight(100)
        self.setTickInterval(interval)
        self.setSingleStep(1)

    def focusInEvent(self, e):
        self.setStyleSheet(slider_style_string)

    def focusOutEvent(self, e):
        self.setStyleSheet(" ")

    def paintEvent(self, e):
        super(LabeledSlider,self).paintEvent(e)
        style=self.style()
        painter=QPainter(self)
        st_slider=QStyleOptionSlider()
        st_slider.initFrom(self)
        st_slider.orientation=self.orientation
        length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self)
        available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self)
        for v, v_str in self.levels:
            rect=painter.drawText(QRect(), Qt.TextDontPrint, v_str)
            y_loc = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), v, available, upsideDown=True)
            bottom = y_loc + length // 2 + rect.height() // 2 + self.top_margin - 3
            left = self.left_margin - rect.width()
            if left <= 0:
                self.left_margin=rect.width()
            pos=QPoint(left, bottom)
            painter.drawText(pos, v_str)
        return

    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key in (Qt.Key_Left, Qt.Key_Right):     # заблокировали стрелки влево-вправо для слайдера
            return
        super().keyPressEvent(keyEvent)



class EqualizerPanel(QWidget):
    def __init__(self, parent = None):
        super(EqualizerPanel, self).__init__(parent)
        self.setStyleSheet("background: #D6EAF8;")
        grid = QGridLayout()
        # left
        left_top_header = QLabel("Коррекция\n <<0>>")
        left_top_header.setStyleSheet("background-color: cyan; padding: 3px 10px 3px 10px;")
        self.left_vertical_slider1 = LabeledSlider(-20, 20 , 10)
        self.left_vertical_slider1.valueChanged.connect(self.__left_slider_1_func)
        self.left_vertical_slider2 = LabeledSlider(-20, 20 , 10)
        self.left_vertical_slider2.valueChanged.connect(self.__left_slider_2_func)
        self.left_vertical_slider3 = LabeledSlider(-20, 20 , 10)
        self.left_vertical_slider3.valueChanged.connect(self.__left_slider_3_func)
        self.left_bottom_label1 = QLabel(str(0))
        self.left_bottom_label1.setFixedWidth(30)
        self.left_bottom_label2 = QLabel(str(0))
        self.left_bottom_label2.setFixedWidth(30)
        self.left_bottom_label3 = QLabel(str(0))
        self.left_bottom_label3.setFixedWidth(30)
        self.left_bottom_label1.setStyleSheet(bottom_label_style)
        self.left_bottom_label2.setStyleSheet(bottom_label_style)
        self.left_bottom_label3.setStyleSheet(bottom_label_style)
        grid.addWidget(left_top_header, 0, 0, 1, 3, alignment=Qt.AlignLeft)
        grid.addWidget(self.left_vertical_slider1, 1, 0)
        grid.addWidget(self.left_vertical_slider2, 1, 1)
        grid.addWidget(self.left_vertical_slider3, 1, 2)
        grid.addWidget(self.left_bottom_label1, 2, 0)
        grid.addWidget(self.left_bottom_label2, 2, 1)
        grid.addWidget(self.left_bottom_label3, 2, 2)
        # center
        center_top_header = QLabel("Поправки\n [ % ]")
        center_top_header.setStyleSheet("background-color: beige; padding: 3px 10px 3px 10px;")
        self.center_vertical_slider1 = LabeledSlider(0, 50, 10)
        self.center_vertical_slider1.valueChanged.connect(self.__center_slider_1_func)
        self.center_vertical_slider2 = LabeledSlider(0, 50, 10)
        self.center_vertical_slider2.valueChanged.connect(self.__center_slider_2_func)
        self.center_vertical_slider3 = LabeledSlider(0, 50, 10)
        self.center_vertical_slider3.valueChanged.connect(self.__center_slider_3_func)
        self.center_bottom_label1 = QLabel(str(0))
        self.center_bottom_label1.setFixedWidth(30)
        self.center_bottom_label2 = QLabel(str(0))
        self.center_bottom_label2.setFixedWidth(30)
        self.center_bottom_label3 = QLabel(str(0))
        self.center_bottom_label3.setFixedWidth(30)
        self.center_bottom_label1.setStyleSheet(bottom_label_style)
        self.center_bottom_label2.setStyleSheet(bottom_label_style)
        self.center_bottom_label3.setStyleSheet(bottom_label_style)
        grid.addWidget(center_top_header, 0, 3, 1, 3, alignment=Qt.AlignCenter)
        grid.addWidget(self.center_vertical_slider1, 1, 3)
        grid.addWidget(self.center_vertical_slider2, 1, 4)
        grid.addWidget(self.center_vertical_slider3, 1, 5)
        grid.addWidget(self.center_bottom_label1, 2, 3)
        grid.addWidget(self.center_bottom_label2, 2, 4)
        grid.addWidget(self.center_bottom_label3, 2, 5)
        # right
        right_top_header = QLabel("Коррекция\n проекта")
        right_top_header.setStyleSheet("background-color: cyan; padding: 3px 10px 3px 10px;")
        self.right_vertical_slider1 = LabeledSlider(-20, 20, 10)
        self.right_vertical_slider1.valueChanged.connect(self.__right_slider_1_func)
        self.right_vertical_slider2 = LabeledSlider(-20, 20, 10)
        self.right_vertical_slider2.valueChanged.connect(self.__right_slider_2_func)
        self.right_bottom_label1 = QLabel(str(0))
        self.right_bottom_label1.setFixedWidth(30)
        self.right_bottom_label2 = QLabel(str(0))
        self.right_bottom_label2.setFixedWidth(30)
        self.right_bottom_label1.setStyleSheet(bottom_label_style)
        self.right_bottom_label2.setStyleSheet(bottom_label_style)
        grid.addWidget(right_top_header, 0, 6, 1, 2,  alignment=Qt.AlignLeft)
        grid.addWidget(self.right_vertical_slider1, 1, 6)
        grid.addWidget(self.right_vertical_slider2, 1, 7)
        grid.addWidget(self.right_bottom_label1, 2, 6)
        grid.addWidget(self.right_bottom_label2, 2, 7)
        self.setLayout(grid)

    def __left_slider_1_func(self, value):
        print('left_bottom_label1 ', value)
        self.left_bottom_label1.setText(str(value))

    def __left_slider_2_func(self, value):
        self.left_bottom_label2.setText(str(value))

    def __left_slider_3_func(self, value):
        self.left_bottom_label3.setText(str(value))

    def __center_slider_1_func(self, value):
        self.center_bottom_label1.setText(str(value))

    def __center_slider_2_func(self, value):
        self.center_bottom_label2.setText(str(value))

    def __center_slider_3_func(self, value):
        self.center_bottom_label3.setText(str(value))

    def __right_slider_1_func(self, value):
        self.right_bottom_label1.setText(str(value))

    def __right_slider_2_func(self, value):
        self.right_bottom_label2.setText(str(value))



app = QApplication(sys.argv)
window = LabeledSlider(-20, 20, 10) #EqualizerPanel()
#window.resize(500, 400)
window.show()
sys.exit(app.exec())