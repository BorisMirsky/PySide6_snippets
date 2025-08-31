from ...common.elements.ArrowPointerIndicator import ArrowPointerIndicator, SizeBoundedWindow
from ..elements.MarkedMultiIndicator import MarkedMultiIndicator
from domain.units.MemoryBufferUnit import MemoryBufferUnit
from domain.units.AbstractUnit import AbstractReadUnit
from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QWidget
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from typing import Optional



class GaugesPanel(SizeBoundedWindow):
    def __init__(self,
        lining_difference_model: AbstractReadUnit[float],
        pendulum_front_difference_model: AbstractReadUnit[float],
        pendulum_work_difference_model: AbstractReadUnit[float],
        pendulum_control_difference_model: AbstractReadUnit[float],
        left_lifting_difference_model: AbstractReadUnit[float],
        right_lifting_difference_model: AbstractReadUnit[float],
        parent: Optional[QWidget] = None):
        super().__init__(0.8, parent)
        self.__lining_difference_model: AbstractReadUnit[float] = lining_difference_model
        self.__pendulum_front_difference_model: AbstractReadUnit[float] = pendulum_front_difference_model
        self.__pendulum_work_difference_model: AbstractReadUnit[float] = pendulum_work_difference_model
        self.__pendulum_control_difference_model: AbstractReadUnit[float] = pendulum_control_difference_model
        self.__left_lifting_difference_model: AbstractReadUnit[float] = left_lifting_difference_model
        self.__right_lifting_difference_model: AbstractReadUnit[float] = right_lifting_difference_model
        self.__lining_difference_model.changed.connect(self.__lining_difference_model_changed)
        self.__pendulum_work_difference_model.changed.connect(self.__pendulum_work_difference_model_changed)
        self.__pendulum_control_difference_model.changed.connect(self.__pendulum_control_difference_model_changed)


        #====================================================================================
        dummy_model = MemoryBufferUnit[float](0.0)
        overlining_difference_model = MemoryBufferUnit[float](0.0)
        empty_difference_model = MemoryBufferUnit[float](0.0)

        self.__left_vertical_slider = MarkedMultiIndicator(dummy_model, self.__left_lifting_difference_model, Qt.Orientation.Vertical, 10)
        self.__left_horizontal_slider = MarkedMultiIndicator(empty_difference_model, overlining_difference_model, Qt.Orientation.Horizontal, 10)
        self.__left_arrow_indicator = ArrowPointerIndicator(chunks = [
            (4, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (1, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (4, Qt.GlobalColor.white),
        ], lineWidth = 1000000)
        self.__left_arrow_indicator.setValueRange(-10, 10)

        left_arrow_view_layout = QGridLayout()
        left_arrow_view_layout.setRowStretch(0, 0)
        left_arrow_view_layout.setRowStretch(1, 1)
        left_arrow_view_layout.setColumnStretch(0, 1)
        left_arrow_view_layout.setColumnStretch(1, 0)
        left_arrow_view_layout.addWidget(self.__left_horizontal_slider, 0, 0, 1, 1)
        left_arrow_view_layout.addWidget(self.__left_vertical_slider, 0, 1, 2, 1)
        left_arrow_view_layout.addWidget(self.__left_arrow_indicator, 1, 0, 1, 1)
        #====================================================================================
        self.__right_vertical_slider = MarkedMultiIndicator(dummy_model, self.__right_lifting_difference_model, Qt.Orientation.Vertical, 10)
        self.__right_horizontal_slider = MarkedMultiIndicator(dummy_model, self.__pendulum_front_difference_model, Qt.Orientation.Horizontal, 10)
        self.__right_arrow_indicator = ArrowPointerIndicator(chunks = [
            (4, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (1, Qt.GlobalColor.white),
            (1, Qt.GlobalColor.red),
            (4, Qt.GlobalColor.white),
        ], lineWidth = 1000000)
        self.__right_small_arrow_indicator = ArrowPointerIndicator(chunks = [
            (2, Qt.GlobalColor.red),
            (7, Qt.GlobalColor.yellow),
            (3, Qt.GlobalColor.green),
            (7, Qt.GlobalColor.yellow),
            (2, Qt.GlobalColor.red),
        ], lineWidth = 4)
        self.__right_small_arrow_indicator.setValueRange(-10, 10)
        self.__right_arrow_indicator.setValueRange(-10, 10)

        right_arrow_view_layout = QGridLayout()
        right_arrow_view_layout.setRowStretch(0, 0)
        right_arrow_view_layout.setRowStretch(1, 1)
        right_arrow_view_layout.setRowStretch(2, 1)
        right_arrow_view_layout.setColumnStretch(6, 0)
        for column in range(6):
            right_arrow_view_layout.setColumnStretch(column, 1)
        right_arrow_view_layout.addWidget(self.__right_horizontal_slider, 0, 0, 1, 6)
        right_arrow_view_layout.addWidget(self.__right_vertical_slider, 0, 6, 3, 1)
        right_arrow_view_layout.addWidget(self.__right_arrow_indicator, 1, 0, 2, 6)
        right_arrow_view_layout.addWidget(self.__right_small_arrow_indicator, 2, 1, 1, 4)
        #====================================================================================
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addLayout(left_arrow_view_layout)
        layout.addLayout(right_arrow_view_layout)

    def __lining_difference_model_changed(self, value: float) ->None:
        self.__left_arrow_indicator.setValue(value or 0.0)
    def __pendulum_work_difference_model_changed(self, value: float) ->None:
        self.__right_arrow_indicator.setValue(value or 0.0)
    def __pendulum_control_difference_model_changed(self, value: float) ->None:
        self.__right_small_arrow_indicator.setValue(value or 0.0)
