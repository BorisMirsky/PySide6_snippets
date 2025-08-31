#This Python file uses the following encoding: utf-8
from domain.dto.Workflow import ProgramTaskCalculationOptionsDto, ProgramTaskCalculationResultDto
from domain.dto.Travelling import PicketDirection, LocationVector1D
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationState, ProgramTaskCalculationOptionsState
from operating.states.lining.ApplicationLiningState import LiningProcessState
from presentation.ui.gui.common.viewes.WindowTitle import Window
from ....utils.store.workflow.zip.Dto import (MeasuringTripResultDto_from_archive,
                                              ProgramTaskCalculationResultDto_to_archive,
                                              ProgramTaskCalculationResultDto_from_archive)
from PySide6.QtWidgets import (QStackedLayout, QWidget, QLabel, QPushButton, QGroupBox, QCheckBox, QComboBox,
                               QDoubleSpinBox, QAbstractSpinBox, QGridLayout, QSpinBox,
                               QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog,
                               QErrorMessage, QComboBox, QDialog, QLineEdit)
from PySide6.QtCore import Qt, QSize, QDateTime, QObject, QCoreApplication, Slot, Signal
from PySide6.QtGui import QFont
import zipfile
import os
import copy


annotations_style = "font: italic; font-size:15px;"           # курсив для комментариев

# ГлавноеМеню -> Расчёт ПЗ ->  НастройкиРасчёта.
class OptionsReconstruction(QWidget):
    closeOptionsReconstructionSignal = Signal(str)
    def __init__(self, restrictions: dict, parent: QWidget = None, 
                 window: Window = None):
        super().__init__(parent)
        self.__restrictions = restrictions
        font = QFont('Arial', 18)
        self.result = copy.deepcopy(self.__restrictions['optimization_parameters'])
        grid = QGridLayout()
        self.__window = window
        #
        lbl1_1 = QLabel('Версия расчёта')
        self.check_box_1 = QCheckBox()
        self.check_box_1.setChecked(False)
        self.check_box_1.stateChanged.connect(self.__checkbox_1_state_changed)
        self.combobox = QComboBox()
        self.combobox.addItems(['Быстрое продвинутое разбиение', 'Без разбиения', 'С разбиением', 'С разбиением v2', 'Продвинутое разбиение'])
        if self.result['calc_plan_version'] == "split":
            self.combobox.setCurrentText("С разбиением")
        if self.result['calc_plan_version'] == "split2":
            self.combobox.setCurrentText("С разбиением v2")
        elif self.result['calc_plan_version'] == "bounded":
            self.combobox.setCurrentText("Без разбиения")
        elif self.result['calc_plan_version'] == "smartsplit":
            self.combobox.setCurrentText("Продвинутое разбиение")
        elif self.result['calc_plan_version'] == "fastsmartsplit":
            self.combobox.setCurrentText("Быстрое продвинутое разбиение")
        self.combobox.setDisabled(False)
        self.combobox.currentTextChanged.connect(self.__calc_plan_version_select_element)
        comment1 = QLabel("Алгоритм расчёта")
        comment1.setStyleSheet(annotations_style)
        grid.addWidget(lbl1_1, 0, 1, 1, 1)
        grid.addWidget(self.combobox, 0, 4, 1, 1)
        grid.addWidget(comment1, 0, 7, 1, 1)
        #
        lbl2_1 = QLabel('Минимальная длина элемента в плане')
        self.check_box_2 = QCheckBox()
        self.check_box_2.setChecked(False)
        self.check_box_2.stateChanged.connect(self.__checkbox_2_state_changed)
        self.spinbox_1 = QSpinBox()
        self.spinbox_1.setRange(5, 50)
        self.spinbox_1.setValue(self.result['min_element_length_plan'])
        self.spinbox_1.setDisabled(True)
        #self.spinbox_1.setFont(font)
        self.spinbox_1.valueChanged.connect(self.__min_element_length_plan_select_element)
        comment2 = QLabel("Ограничение на минимальную длину элемента для плана.\n Значения от 5 до 50.")
        comment2.setStyleSheet(annotations_style)
        grid.addWidget(lbl2_1, 1, 1, 1, 1)
        grid.addWidget(self.check_box_2, 1, 3, 1, 1)
        grid.addWidget(self.spinbox_1, 1, 4, 1, 1)
        grid.addWidget(comment2, 1, 7, 1, 1)
        #
        lbl3_1 = QLabel('Минимальная длина элемента в профиле')
        self.check_box_3 = QCheckBox()
        self.check_box_3.setChecked(False)
        self.check_box_3.stateChanged.connect(self.__checkbox_3_state_changed)
        self.spinbox_2 = QSpinBox()
        self.spinbox_2.setRange(3, 50)
        self.spinbox_2.setValue(self.result['min_element_length_prof'])
        self.spinbox_2.setDisabled(True)
        #self.spinbox_2.setFont(font)
        self.spinbox_2.valueChanged.connect(self.__min_element_length_prof_select_element)
        comment3 = QLabel("Ограничение на минимальную длину элемента для профиля.\n Значения от 3 до 50.")
        comment3.setStyleSheet(annotations_style)
        grid.addWidget(lbl3_1, 2, 1, 1, 1)
        grid.addWidget(self.check_box_3, 2, 3, 1, 1)
        grid.addWidget(self.spinbox_2, 2, 4, 1, 1)
        grid.addWidget(comment3, 2, 7, 1, 1)
        #
        lbl4_1 = QLabel('Значение стрелы')
        self.check_box_4 = QCheckBox()
        self.check_box_4.setChecked(False)
        self.check_box_4.stateChanged.connect(self.__checkbox_4_state_changed)
        self.spinbox_3 = QSpinBox()
        self.spinbox_3.setRange(0, 100)
        self.spinbox_3.setValue(self.result['plan_min_value'])
        self.spinbox_3.setDisabled(True)
        #self.spinbox_3.setFont(font)
        self.spinbox_3.valueChanged.connect(self.__plan_min_value_select_element)
        comment4 = QLabel("Если значение стрелы на симметричной хорде 10 \nбольше заданного числа и 100 раз подряд, то считаем, что начало кривой. \nНужно когда стрелы ненулевые на прямых участках.")
        comment4.setStyleSheet(annotations_style)
        grid.addWidget(lbl4_1, 3, 1, 1, 1)
        grid.addWidget(self.check_box_4, 3, 3, 1, 1)
        grid.addWidget(self.spinbox_3, 3, 4, 1, 1)
        grid.addWidget(comment4, 3, 7, 1, 1)
        #
        lbl5_1 = QLabel('ВНР для прямого участка')
        self.check_box_5 = QCheckBox()
        self.check_box_5.setChecked(False)
        self.check_box_5.stateChanged.connect(self.__checkbox_5_state_changed)
        self.combobox_4 = QComboBox()
        for i in range(-150, 151, 1):
            self.combobox_4.addItem(str(i))
        self.combobox_4.addItem('Значение отсутствует')
        if self.result['straight_urov'] is None:
            self.combobox_4.setCurrentText('Значение отсутствует') #self.result['straight_urov'])
        self.combobox_4.setDisabled(True)
        #self.combobox_4.setFont(font)
        self.combobox_4.currentTextChanged.connect(self.__straight_urov_select_element)
        comment5 = QLabel("Задает уровень для прямого участка. \nИмеет смысл если у нас полностью прямой участок.")
        comment5.setStyleSheet(annotations_style)
        grid.addWidget(lbl5_1, 4, 1, 1, 1)
        grid.addWidget(self.check_box_5, 4, 3, 1, 1)
        grid.addWidget(self.combobox_4, 4, 4, 1, 1)
        grid.addWidget(comment5, 4, 7, 1, 1)
        #
        okButton = QPushButton("Ok")
        okButton.setProperty("optionsWindowPushButton", True)
        okButton.clicked.connect(self.__handleOkButton)
        #
        exitButton = QPushButton("Выход")
        exitButton.setProperty("optionsWindowPushButton", True)
        exitButton.clicked.connect(self.__closeThisPage)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(okButton, 5, 1, 2, 5)
        grid.addWidget(exitButton, 7, 1, 2, 5)
        self.setLayout(grid)
        self.__window.setTitle("Расчёт программного задания > Настройки алгоритма расчёта")

    def __checkbox_1_state_changed(self, state):
        if state == 2:
            self.combobox.setDisabled(False)
        else:
            self.combobox.setDisabled(True)

    def __checkbox_2_state_changed(self, state):
        if state == 2:
            self.spinbox_1.setDisabled(False)
        else:
            self.spinbox_1.setDisabled(True)

    def __checkbox_3_state_changed(self, state):
        if state == 2:
            self.spinbox_2.setDisabled(False)
        else:
            self.spinbox_2.setDisabled(True)

    def __checkbox_4_state_changed(self, state):
        if state == 2:
            self.spinbox_3.setDisabled(False)
        else:
            self.spinbox_3.setDisabled(True)

    def __checkbox_5_state_changed(self, state):
        if state == 2:
            self.combobox_4.setDisabled(False)
        else:
            self.combobox_4.setDisabled(True)

    #=============================================================
    def __closeThisPage(self):
        self.closeOptionsReconstructionSignal.emit('close')

    def __calc_plan_version_select_element(self, selected:str):
        if selected == "Без разбиения":
            self.result["calc_plan_version"] = "bounded"
        elif selected == "С разбиением":
            self.result["calc_plan_version"] = "split"
        elif selected == "С разбиением v2":
            self.result["calc_plan_version"] = "split2"
        elif selected == "Продвинутое разбиение":
            self.result["calc_plan_version"] = "smartsplit"
        elif selected == "Быстрое продвинутое разбиение":
            self.result["calc_plan_version"] = "fastsmartsplit"

    def __min_element_length_plan_select_element(self, selected:str):
        self.result["min_element_length_plan"] = selected

    def __min_element_length_prof_select_element(self, selected:str):
        self.result["min_element_length_prof"] = selected

    def __plan_min_value_select_element(self, selected:str):
        self.result["plan_min_value"] = selected

    def __straight_urov_select_element(self, selected:str):
        self.result["straight_urov"] = int(selected)

    def __handleOkButton(self):
        #print(self.result)
        self.__restrictions['optimization_parameters']['calc_plan_version'] = self.result['calc_plan_version']
        self.__restrictions['optimization_parameters']['min_element_length_plan'] = self.result['min_element_length_plan']
        self.__restrictions['optimization_parameters']['min_element_length_prof'] = self.result['min_element_length_prof']
        self.__restrictions['optimization_parameters']['plan_min_value'] = self.result['plan_min_value']
        if self.result['straight_urov'] == 'Значение отсутствует':
            self.__restrictions['optimization_parameters']['straight_urov'] = None
        else:
            self.__restrictions['optimization_parameters']['straight_urov'] == self.result['straight_urov']
        #
        self.closeOptionsReconstructionSignal.emit('close')


