from PySide6.QtWidgets import (QWidget, QLabel,QGridLayout,QSpinBox,QRadioButton,QPushButton,QLineEdit,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QDialog)
from PySide6.QtGui import QFont, Qt, QColor, QDoubleValidator
from PySide6.QtCore import Qt, QObject
import sys
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationOptionsState
from domain.calculations.helpers import normative_slope_by_velocity
from typing import Optional
import json



class WindowSettingsRestrictions(QWidget):
    def __init__(self, restrictions: dict, parent: Optional[QWidget] = None) ->None:
        super(WindowSettingsRestrictions, self).__init__(parent)
        self.__edited_restrictions = json.loads(json.dumps(restrictions))
        #self.setMinimumHeight(700)
        #self.setMinimumWidth(600)
        wrapping_groupbox_header = "Настройки расчёта" # "Установки ограничений"
        #
        wrapping_groupbox = QGroupBox(wrapping_groupbox_header, alignment=Qt.AlignHCenter)
        wrapping_groupbox.setObjectName('wrapping_groupbox')
        self.wrapping_groupbox_layout = QVBoxLayout()
        wrapping_groupbox.setLayout(self.wrapping_groupbox_layout)
        #
        groupbox_speed_title = "Допустимые скоростные характеристики"     #"Скорости"
        groupbox_speed = QGroupBox(groupbox_speed_title, alignment=Qt.AlignHCenter)
        groupbox_speed_grid = QGridLayout()
        groupbox_speed_label_pass = QLabel("Пассажирские поезда, максимальная км/ч")
        groupbox_speed_label_gruz = QLabel("Грузовые поезда, максимальная км/ч")
        groupbox_speed_label_angle_deviation = QLabel("Уклон отвода мм/м")
        groupbox_speed_spinbox_pass = QSpinBox()
        groupbox_speed_spinbox_pass.setRange(0, 250)
        groupbox_speed_spinbox_pass.setValue(self.__edited_restrictions['segments'][0]['v_pass'])
        groupbox_speed_spinbox_pass.valueChanged.connect(self.__update_speed_spinbox_pass)
        groupbox_speed_spinbox_gruz = QSpinBox()
        groupbox_speed_spinbox_gruz.setRange(0, 1000)
        groupbox_speed_spinbox_gruz.setValue(self.__edited_restrictions['segments'][0]['v_gruz'])
        groupbox_speed_spinbox_gruz.valueChanged.connect(self.__update_speed_spinbox_gruz)
        # Уклон отвода по дефолту
        self.angle_deviation = normative_slope_by_velocity(self.__edited_restrictions['segments'][0]['v_pass'])
        self.groupbox_speed_lineedit_angle_deviation = QLineEdit(str(self.angle_deviation))
        self.groupbox_speed_lineedit_angle_deviation.setProperty('optionsWindowLineEdit', True)
        self.groupbox_speed_lineedit_angle_deviation.setReadOnly(True)
        groupbox_speed_grid.addWidget(groupbox_speed_label_pass, 0, 0)
        groupbox_speed_grid.addWidget(groupbox_speed_spinbox_pass, 0, 1)
        groupbox_speed_grid.addWidget(groupbox_speed_label_gruz, 1, 0)
        groupbox_speed_grid.addWidget(groupbox_speed_spinbox_gruz, 1, 1)
        groupbox_speed_grid.addWidget(groupbox_speed_label_angle_deviation, 2, 0)
        groupbox_speed_grid.addWidget(self.groupbox_speed_lineedit_angle_deviation, 2, 1)
        groupbox_speed.setLayout(groupbox_speed_grid)
        #
        groupbox_restrictions_title = "Ограничения смещения пути"   # продольного/поперечного
        groupbox_restrictions = QGroupBox(groupbox_restrictions_title, alignment=Qt.AlignHCenter)
        groupbox_restrictions_hbox = QHBoxLayout()
        groupbox_restrictions.setLayout(groupbox_restrictions_hbox)
        #
        groupbox_restrictions_shifts_title = "Сдвижка мм"
        groupbox_restrictions_shifts = QGroupBox(groupbox_restrictions_shifts_title, alignment=Qt.AlignHCenter)
        groupbox_restrictions_shifts_grid = QGridLayout()
        groupbox_restrictions_shifts_grid_label_right = QLabel("Право (-)")
        groupbox_restrictions_shifts_grid_label_left = QLabel("Лево (+)")
        groupbox_restrictions_shifts_spinbox_right = QSpinBox()
        groupbox_restrictions_shifts_spinbox_right.setRange(-1000, 1000)
        groupbox_restrictions_shifts_spinbox_right.setValue(self.__edited_restrictions['segments'][0]['shifting_right'])
        groupbox_restrictions_shifts_spinbox_right.valueChanged.connect(self.__update_restrictions_shifts_spinbox_right)
        groupbox_restrictions_shifts_spinbox_left = QSpinBox()
        groupbox_restrictions_shifts_spinbox_left.setRange(-1000, 1000)
        groupbox_restrictions_shifts_spinbox_left.setValue(self.__edited_restrictions['segments'][0]['shifting_left'])
        groupbox_restrictions_shifts_spinbox_left.valueChanged.connect(self.__update_restrictions_shifts_spinbox_left)
        groupbox_restrictions_shifts_grid.addWidget(groupbox_restrictions_shifts_grid_label_right, 0, 0)
        groupbox_restrictions_shifts_grid.addWidget(groupbox_restrictions_shifts_spinbox_right, 0, 1)
        groupbox_restrictions_shifts_grid.addWidget(groupbox_restrictions_shifts_grid_label_left, 1, 0)
        groupbox_restrictions_shifts_grid.addWidget(groupbox_restrictions_shifts_spinbox_left, 1, 1)
        groupbox_restrictions_shifts.setLayout(groupbox_restrictions_shifts_grid)
        #
        groupbox_restrictions_lifting_title = "Подъёмка мм"
        groupbox_restrictions_lifting = QGroupBox(groupbox_restrictions_lifting_title, alignment=Qt.AlignHCenter)
        groupbox_restrictions_lifting_grid = QGridLayout()
        groupbox_restrictions_lifting_label_max = QLabel("Максимальная")
        groupbox_restrictions_lifting_label_min = QLabel("Минимальная")
        groupbox_restrictions_lifting_spinbox_max = QSpinBox()
        groupbox_restrictions_lifting_spinbox_max.setRange(-1000, 1000)
        groupbox_restrictions_lifting_spinbox_max.setValue(self.__edited_restrictions['segments'][0]['raising_ubound'])
        groupbox_restrictions_lifting_spinbox_max.valueChanged.connect(self.__update_restrictions_lifting_spinbox_max)
        groupbox_restrictions_lifting_spinbox_min = QSpinBox()
        groupbox_restrictions_lifting_spinbox_min.setRange(-1000, 1000)
        groupbox_restrictions_lifting_spinbox_min.setValue(self.__edited_restrictions['segments'][0]['raising_lbound'])
        groupbox_restrictions_lifting_spinbox_min.valueChanged.connect(self.__update_restrictions_lifting_spinbox_min)
        groupbox_restrictions_lifting_grid.addWidget(groupbox_restrictions_lifting_label_max, 0, 0)
        groupbox_restrictions_lifting_grid.addWidget(groupbox_restrictions_lifting_spinbox_max, 0, 1)
        groupbox_restrictions_lifting_grid.addWidget(groupbox_restrictions_lifting_label_min, 1, 0)
        groupbox_restrictions_lifting_grid.addWidget(groupbox_restrictions_lifting_spinbox_min, 1, 1)
        groupbox_restrictions_lifting.setLayout(groupbox_restrictions_lifting_grid)
        # пока не используем
        # rb = QRadioButton()
        # rb_label = QLabel("Прямая вставка")
        # rb_label.setAlignment(Qt.AlignLeft)
        # rb_hbox = QHBoxLayout()
        # rb_hbox.addWidget(rb)
        # rb_hbox.addWidget(rb_label)
    #    ok_button = QPushButton("OK")
    #    ok_button.setMaximumWidth(100)
    #    ok_button.clicked.connect(self.accept)
        groupbox_restrictions_hbox.addWidget(groupbox_restrictions_shifts)
        groupbox_restrictions_hbox.addWidget(groupbox_restrictions_lifting)
        #
        #info_label = QLabel("Перемещение по меню клавишей 'tab'. Изменение параметров стрелками либо числовым вводом.")
        #info_label.setAlignment(Qt.AlignHCenter)
        #info_label.setWordWrap(True)
        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.wrapping_groupbox_layout.setSpacing(20)
        self.wrapping_groupbox_layout.addWidget(groupbox_speed)
        self.wrapping_groupbox_layout.addWidget(groupbox_restrictions)
        #self.wrapping_groupbox_layout.addWidget(ok_button)                  # пока что не используется
        #self.wrapping_groupbox_layout.addWidget(info_label)
        #self.wrapping_groupbox_layout.insertWidget(2, groupbox_speed)
        #self.wrapping_groupbox_layout.insertWidget(3, groupbox_restrictions)
        #self.wrapping_groupbox_layout.insertWidget(4, info_label)
        vbox.addWidget(wrapping_groupbox)
        self.setLayout(vbox)

    # def __okButtonFunction(self) ->None:
    #     print('groupbox_speed_lineedit_angle_deviation: ', self.groupbox_speed_lineedit_angle_deviation.text())
    #     print('копия конфига ограничений: ', self.__edited_restrictions)
    #     #self.__edited_restrictions['segments'][0]['___???___'] = value           # ?!?!
    #     #return self.__edited_restrictions
    #     self.close()

    def edited_restrictions(self) ->dict:
        return self.__edited_restrictions
    def __update_speed_spinbox_pass(self, value):
        self.__edited_restrictions['segments'][0]['v_pass'] = value
        self.angle_deviation = normative_slope_by_velocity(value)
        self.groupbox_speed_lineedit_angle_deviation.setText(str(self.angle_deviation))
    def __update_speed_spinbox_gruz(self, value):
        self.__edited_restrictions['segments'][0]['v_gruz'] = value
    def __update_restrictions_shifts_spinbox_right(self, value):
        self.__edited_restrictions['segments'][0]['shifting_right'] = value
    def __update_restrictions_shifts_spinbox_left(self, value):
        self.__edited_restrictions['segments'][0]['shifting_left'] = value
    def __update_restrictions_lifting_spinbox_max(self, value):
        self.__edited_restrictions['segments'][0]['raising_ubound'] = value
    def __update_restrictions_lifting_spinbox_min(self, value):
        self.__edited_restrictions['segments'][0]['raising_lbound'] = value

