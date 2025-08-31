
from .Slider import LabeledSlider
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.MemoryBufferUnit import MemoryBufferUnit
from operating.states.lining.ApplicationLiningState import LiningProcessState
from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtGui import QColor,QFocusEvent
from PySide6.QtCore import Qt
from typing import Optional
import sys


bottom_label_style = """ border :1px solid; border-color: black; font: 15px; """
#padding-left:8px; padding-right:8px; padding-right:5px; padding-bottom:5px;"""#padding: 2px 2px 2px 2px;"""

#dummy_model = MemoryBufferUnit[float](0.0)
class EqualizerPanel(QWidget):
    def __init__(self,
                 unit1: AbstractReadWriteUnit[float],
                 unit2: AbstractReadWriteUnit[float],
                 unit3: AbstractReadWriteUnit[float],
                 unit4: AbstractReadWriteUnit[float],
                 unit5: AbstractReadWriteUnit[float],
                 unit6: AbstractReadWriteUnit[float],
                 unit7: AbstractReadWriteUnit[float],
                 unit8: AbstractReadWriteUnit[float],
                 parent = None):
        super(EqualizerPanel, self).__init__(parent)
        self.slider1_unit: AbstractReadWriteUnit[float] = unit1
        self.slider2_unit: AbstractReadWriteUnit[float] = unit2
        self.slider3_unit: AbstractReadWriteUnit[float] = unit3
        self.slider4_unit: AbstractReadWriteUnit[float] = unit4
        self.slider5_unit: AbstractReadWriteUnit[float] = unit5
        self.slider6_unit: AbstractReadWriteUnit[float] = unit6
        self.slider7_unit: AbstractReadWriteUnit[float] = unit7
        self.slider8_unit: AbstractReadWriteUnit[float] = unit8
        #
        self.setStyleSheet("background: #D6EAF8;")
        grid = QGridLayout()
        # left
        left_top_header = QLabel("Коррекция\n <<0>>")
        left_top_header.setStyleSheet("background-color: cyan; padding: 3px 10px 3px 10px;")
        self.left_vertical_slider1 = LabeledSlider(self.slider1_unit,
                                                     -40, 40 , 20, 20)
        self.left_vertical_slider1.valueChanged.connect(self.__left_slider_1_func)
        self.left_vertical_slider2 = LabeledSlider(self.slider2_unit,
                                                     -40, 40 , 20, 20)
        self.left_vertical_slider2.valueChanged.connect(self.__left_slider_2_func)
        self.left_vertical_slider3 = LabeledSlider(self.slider3_unit,
                                                     -40, 40 , 20, 20)
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
        self.center_vertical_slider1 = LabeledSlider(self.slider4_unit,
                                                       0, 50, 10, 10)
        self.center_vertical_slider1.valueChanged.connect(self.__center_slider_1_func)
        self.center_vertical_slider2 = LabeledSlider(self.slider5_unit,
                                                       0, 50, 10, 10)
        self.center_vertical_slider2.valueChanged.connect(self.__center_slider_2_func)
        self.center_vertical_slider3 = LabeledSlider(self.slider6_unit,
                                                       0, 50, 10, 10)
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
        self.right_vertical_slider1 = LabeledSlider(self.slider7_unit,
                                                      -20, 20, 10, 10)
        self.right_vertical_slider1.valueChanged.connect(self.__right_slider_1_func)
        self.right_vertical_slider2 = LabeledSlider(self.slider8_unit,
                                                      -20, 20, 10, 10)
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

   # ========================= Методы выставляют значения внизу и окрашивают слайдер ==================================
    # equalizer.left_vertical_slider1.valueChanged.connect(self.__state.lining_adjustment().write)
    # equalizer.left_vertical_slider2.valueChanged.connect(self.__state.raising_adjustment().write)
    # equalizer.left_vertical_slider3.valueChanged.connect(self.__state.vozv_adjustment().write)

    def __left_slider_1_func(self, value):
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
