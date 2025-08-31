from PySide6.QtWidgets import (QHBoxLayout, QGridLayout, QWidget, QVBoxLayout, QLabel,
                               QApplication, QSlider, QStyleOptionSlider, QStyle)
from PySide6.QtGui import QColor, QPainter, QFocusEvent
from PySide6.QtCore import Qt, QPoint, QRect
#from domain.units.AbstractUnit import AbstractReadWriteUnit, AbstractReadUnit
import sys

# handle - ползунок, groove - желоб, фон
slider_style_string1 = """
            QSlider::handle:vertical {
                height: 10px;
                width: 10px;
                background-color: #C0392B;
                }
            QSlider::groove:vertical {
                background: #F4D03F;
            }
    """

slider_style_string = """
       QSlider::TicksRight
"""

# class LabeledSlider(QSlider):
#     def __init__(self,
#                  #model: AbstractReadWriteUnit[float],
#                  minimum: int, maximum:int, interval:int, value:int,
#                  parent=None):
#         super(LabeledSlider, self).__init__(parent=parent)
#         levels=range(minimum, maximum+interval, interval)
#         #self.__model = model
#         self.value = value
#         self.valueChanged.connect(self.__value_changed)
#         self.levels=list(zip(levels, map(str, levels)))
#         self.left_margin, self.top_margin, self.right_margin, self.bottom_margin = 10, 10, 10, 10
#         self.orientation = Qt.Vertical
#         self.setEnabled(True)
#         self.setMinimum(minimum)
#         self.setMaximum(maximum)
#         self.setTickPosition(QSlider.TicksRight)
#         self.setMinimumHeight(100)
#         self.setTickInterval(interval)
#         self.setSingleStep(1)
#
#     def focusInEvent(self, e):
#         self.setStyleSheet(slider_style_string)
#
#     def focusOutEvent(self, e):
#         self.setStyleSheet(" ")
#
#     def __value_changed(self, value):
#         print(value)
#         #self.__model.write(value)
#     #
#     def paintEvent(self, e):
#         super(LabeledSlider,self).paintEvent(e)
#         style=self.style()
#         painter=QPainter(self)
#         st_slider=QStyleOptionSlider()
#         st_slider.initFrom(self)
#         st_slider.orientation=self.orientation
#         length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self)
#         available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self)
#         for v, v_str in self.levels:
#             rect=painter.drawText(QRect(), Qt.TextDontPrint, v_str)
#             y_loc=QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), v, available, upsideDown=True)
#             bottom=y_loc+length//2+rect.height()//2+self.top_margin-3
#             left=self.left_margin - rect.width()
#             if left<=0:
#                 self.left_margin=rect.width()
#             pos=QPoint(left, bottom)
#             painter.drawText(pos, v_str)
#         return
#
#     # def keyPressEvent(self, keyEvent):
#     #     key = keyEvent.key()
#     #     if key in (Qt.Key_Left, Qt.Key_Right):     # заблокировали стрелки влево-вправо для слайдера
#     #         return
#     #     super().keyPressEvent(keyEvent)



class LabeledSlider1(QWidget):
    def __init__(self,
                 minimum:int, maximum:int, value:int, interval=10,
                 orientation=Qt.Vertical, parent=None):
        super(LabeledSlider1, self).__init__(parent=parent)
        levels=range(minimum, maximum+interval, interval)
        self.levels=list(zip(levels,map(str,levels)))
        print('self.levels ', self.levels)
        self.value = value
        self.left_margin=0
        self.top_margin=0
        self.right_margin=0
        self.bottom_margin=0
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(self.left_margin,self.top_margin,
                self.right_margin,self.bottom_margin)
        self.sl=QSlider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        self.sl.setValue(minimum)
        self.sl.valueChanged.connect(self.__value_changed)
        self.sl.setTickPosition(QSlider.TicksLeft)
        self.sl.setMinimumHeight(100)
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)
        self.layout.addWidget(self.sl)

    def focusInEvent(self, e):
        #print("focusInEvent from slider", e)
        self.sl.setStyleSheet(slider_style_string)

    def focusOutEvent(self, e):
        #print("focusOutEvent from slider", e)
        self.sl.setStyleSheet(" ")

    def __value_changed(self, value):
        pass
        #print("value ", value)
        #self.__model.write(value)

    def paintEvent(self, e):
        super(LabeledSlider1,self).paintEvent(e)
        style=self.sl.style()
        painter=QPainter(self)
        st_slider=QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation=self.sl.orientation()
        length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)
        #print('length ', length, 'available ', available)
        for v, v_str in self.levels:
            rect=painter.drawText(QRect(), Qt.TextDontPrint, v_str)
            y_loc=QStyle.sliderPositionFromValue(self.sl.minimum(), self.sl.maximum(), v, available, upsideDown=True)
            bottom=y_loc+length//2+rect.height()//2+self.top_margin-3
            left=self.left_margin-rect.width()
            if left<=0:
                self.left_margin=rect.width()+2
                self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)
            pos=QPoint(left, bottom)
            painter.drawText(pos, v_str)
            #print('rect ', rect, 'y_loc ', y_loc, 'bottom ', bottom, 'left ', left, 'pos ', pos)
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame=QWidget()
    hbox=QHBoxLayout()
    frame.setLayout(hbox)
    slider1 = LabeledSlider1(-20, 20 , 10, 10)
    slider1.show()
    hbox.addWidget(slider1)
    frame.show()
    sys.exit(app.exec())