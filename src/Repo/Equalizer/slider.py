from PySide6.QtWidgets import (QHBoxLayout, QGridLayout, QWidget, QVBoxLayout, QLabel, QApplication, QSlider, QStyleOptionSlider,
                               QStyle)
from PySide6.QtGui import QColor, QPainter, QFocusEvent
from PySide6.QtCore import Qt, QPoint, QRect
#from domain.units.AbstractUnit import AbstractReadWriteUnit, AbstractReadUnit
import sys

# handle - ползунок, groove - желоб, фон
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
    def __init__(self,
                 minimum: int, maximum:int,  value:int,
                 interval=10, parent=None):
        super(LabeledSlider, self).__init__(parent=parent)
        levels=range(minimum, maximum+interval, interval)
        self.value = value
        self.setContentsMargins(20,20,20,20)
        self.levels=list(zip(levels, map(str, levels)))
        self.left_margin, self.top_margin, self.right_margin, self.bottom_margin = 20, 20, 20, 20
        self.orientation = Qt.Vertical
        self.setEnabled(True)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setTickPosition(QSlider.TicksRight)
        self.setMinimumHeight(120)
        self.setTickInterval(interval)
        self.setSingleStep(1)

    def focusInEvent(self, e):
        self.setStyleSheet(slider_style_string)

    def focusOutEvent(self, e):
        self.setStyleSheet(" ")

    def paintEvent(self, e):
        super(LabeledSlider,self).paintEvent(e)
        style = self.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self)
        st_slider.orientation=self.orientation
        length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self)
        print(length)
        available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self)
        for v, v_str in self.levels:
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)
            y_loc = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), v, available, upsideDown=True)
            bottom = y_loc + length//2 + rect.height() // 2 - 3
            left = self.left_margin - rect.width()
            if left <= 0:
                self.left_margin = rect.width()
            pos = QPoint(left, bottom)
            #print(v, y_loc, left, bottom)
            painter.drawText(pos, v_str)
        return

    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        if key in (Qt.Key_Left, Qt.Key_Right):     # заблокировали стрелки влево-вправо для слайдера
            return
        super().keyPressEvent(keyEvent)




app = QApplication(sys.argv)
slider1 = LabeledSlider(-20, 20 , 10)
#window.resize(500, 400)
slider1.show()


# sys.exit(app.exec())
