
from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,QTextEdit,QStackedWidget,QLabel,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton, QSpinBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize, Slot
import sys
import copy
from ServiceInfo import *
from Charts import Chart1
from VerticalLine import VerticalLineModel, MoveLineController



class BottomWidget(QWidget):
    updatedCounterSignal = Signal(int)
    def __init__(self, model1:VerticalLineModel,
                 model2:VerticalLineModel,
                 model3:VerticalLineModel):
        super().__init__()
        #
        self.counter = 0
        self.groupbox1_title = ""
        groupbox2_title = "Переустройство"
        self.groupbox1 = QGroupBox(self.groupbox1_title, alignment=Qt.AlignHCenter)
        self.groupbox2 = QGroupBox(groupbox2_title, alignment=Qt.AlignHCenter)
        self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;}")
        self.groupbox2.setStyleSheet("QGroupBox{font-size: 18px;font-weight: bold;}")
        self.vbox_groupbox1 = QVBoxLayout()
        self.vbox_groupbox2 = QVBoxLayout()
        self.groupbox1.setLayout(self.vbox_groupbox1)
        self.groupbox2.setLayout(self.vbox_groupbox2)
        #
        self.pandasModel = PandasModel
        self.myTable = MyTable
        #
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.vertical_model3 = model3
        self.lineMover1 = MoveLineController(0, self.vertical_model1, self.vertical_model2, self.vertical_model3)
        #self.installEventFilter(self.lineMover1)
        self.lineMover2 = MoveLineController(0, self.vertical_model1, self.vertical_model2, self.vertical_model3)
        #self.installEventFilter(self.lineMover2)
        self.lineMover3 = MoveLineController(0, self.vertical_model1, self.vertical_model2, self.vertical_model3)
        self.topChart = Chart1('plan_prj', 'plan_fact', self.vertical_model1, self.vertical_model2, self.vertical_model3)
        #
        self.Stack1 = QStackedWidget()
        self.__fillFirstStackwidget(SUMMARYFILENAME)
        self.vbox_groupbox1.addWidget(self.Stack1)
        #
        self.Stack2 = QStackedWidget()
        self.Stack2.setMaximumHeight(110)
        self.fill_second_stackwidget(SUMMARYFILENAME)
        self.vbox_groupbox2.addWidget(self.Stack2)
        self.vbox_groupbox2.addStretch(2)
        self.selected_function_shortcut = QShortcut(Qt.Key_Return, self)             # выбор клавиший 'enter'
        self.selected_function_shortcut.activated.connect(lambda: self.__selectedReconstructionFunction(self.counter))
        #
        self.transitionTempVerticalFirstLineTopLevel = round(get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185)
        self.transitionTempVerticalSecondLineTopLevel = round(get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185)
        self.Stack3 = QStackedWidget()
        #self.fill_third_stackwidget()
        self.vbox_groupbox2.addWidget(self.Stack3)
        self.Stack3.hide()
        #self.lengthValue = str(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][2] / 0.185))
        #
        #self.len_current_distance = get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'transition':

        # пока не надо - закрытие окна по второму esc
        #self.close_window_shortcut = QShortcut(Qt.Key_Escape, self)
        #self.close_window_shortcut.activated.connect(lambda: self.close())
        #
        self.button_to_left = QToolButton(self.groupbox1) 
        self.button_to_left.setIcon(QIcon("Data/left-arrow.png"))
        self.button_to_left.setIconSize(QSize(22, 22))
        self.button_to_left.setFixedSize(QSize(25, 25))
        self.button_to_left.clicked.connect(self.__handleLeftButton)
        self.button_to_right = QToolButton(self.groupbox1) 
        self.button_to_right.setIcon(QIcon("Data/right-arrow.png"))
        self.button_to_right.setIconSize(QSize(22, 22))
        self.button_to_right.setFixedSize(QSize(25, 25))
        self.button_to_right.clicked.connect(self.__handleRightButton)
        #
        self.textEdit = QTextEdit()
        self.textEdit.append("Откат: Ctrl + Backspace\n")
        self.textEdit.append("Количество изменений: 696\n")
        self.textEdit.append("Перемещение по странице клавишей 'tab' либо стрелками\n")
        self.textEdit.append("Изменение масштаба графика кнопками 'W' и 'S'\n")
        self.textEdit.append("Перемещение по графику кнопками-стрелками\n")
        self.textEdit.append("Смещение графика по оси OX клавишами 'A' и 'D'\n")
        self.textEdit.append("Выбор функции переустройства клавишей 'Enter'\n")
        self.textEdit.setFocusPolicy(Qt.NoFocus)
        #
        hbox = QHBoxLayout()
        hbox.addWidget(self.groupbox1, 1)
        hbox.addWidget(self.groupbox2, 1)
        hbox.addWidget(self.textEdit, 1)
        self.setLayout(hbox)

    # заполнение данными первого блока "тип кривой + таблица с данными из Summary"
    # запускается сразу и один раз
    def __fillFirstStackwidget(self, summary: str):
        for i in range(0, SUMMARY_LEN, 1):
            self.table = MyTable(PandasModel, getRowFromSummary(summary, i))
            self.Stack1.addWidget(self.table)
            
    # заполнение данными второго блока "функции переустройства"
    # запускается сразу и один раз
    def fill_second_stackwidget(self, summary: str):
        data = read_csv_file(summary)
        listwidget_font = QFont()
        listwidget_font.setPixelSize(18)
        for i in range(0, SUMMARY_LEN, 1):
            self.list_widget = QListWidget()
            self.list_widget.setFont(listwidget_font)
            row = data.iloc[[i]]
            if row.values.tolist()[0][-1] == 'transition':
                self.list_widget.addItems(['Изменить Lпк', 'Разделить ПК', 'Сместить ПК', 'Исключить ПК'])
                object_name = 'transition' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            elif row.values.tolist()[0][-1] == 'curve':
                self.list_widget.addItems(['Изменить радиус', 'Изменить длину'])
                object_name = 'curve' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            elif row.values.tolist()[0][-1] == 'straight':
                self.list_widget.addItems(['', '',''])
                object_name = 'straight' + ' ' + str(i)
                self.list_widget.setObjectName(object_name)
                self.Stack2.addWidget(self.list_widget)
            #self.Stack2.addWidget(self.list_widget)


    # заполнение данными третьего блока "применение выбранной функции переустройства"
    # запускается сразу и один раз
    # def fill_third_stackwidget(self):
    #     funcs_list = [['Изменить Lпк', 'Длина'], ['Разделить ПК', ''], ['Сместить ПК', 'Положение'],
    #                  ['Исключить ПК', ''],['Изменить радиус', 'Радиус'], ['Изменить длину', 'Длина']]
    #     for func in funcs_list:
    #         if func == ['Изменить Lпк', 'Длина']:    # пока что сделано как особый случай
    #             widget = self.__transitionChangeLength(self.counter)
    #             self.Stack3.addWidget(widget)
    #         else:
    #             widget = self.input_data_widget(func[1])     # заглушка
    #             self.Stack3.addWidget(widget)
                

    # выбор функции переустройства
    def __selectedReconstructionFunction(self, idx):
        if self.Stack2.widget(idx).currentItem().text() == 'Изменить Lпк':
            changeLengthWidget = self.__transitionChangeLength(idx)
            self.Stack3.addWidget(changeLengthWidget)
            #self.Stack3.setCurrentIndex(0)
            self.Stack3.setCurrentWidget(changeLengthWidget)
            self.Stack3.show()
            self.lineMover3.eventFilter('hide')
        elif self.Stack2.widget(idx).currentItem().text() == 'Разделить ПК':
            self.Stack3.hide()
            self.__transitionDivideLength(idx)
        elif self.Stack2.widget(idx).currentItem().text() == 'Сместить ПК':
            chiftWidget = self.__transitionShift(idx)
            self.Stack3.addWidget(chiftWidget)
            self.Stack3.setCurrentWidget(chiftWidget)
            self.Stack3.show()
            self.lineMover3.eventFilter('hide')
        elif self.Stack2.widget(idx).currentItem().text() == 'Исключить ПК':
            self.Stack3.hide()
            self.lineMover3.eventFilter('hide')
        elif self.Stack2.widget(idx).currentItem().text() == 'Изменить радиус':
            curveChangeRadius = self.__curveChangeRadius(idx)
            self.Stack3.addWidget(curveChangeRadius)
            #self.Stack3.setCurrentIndex(2)
            self.Stack3.setCurrentWidget(curveChangeRadius)
            self.Stack3.show()
            self.lineMover3.eventFilter('hide')
        elif self.Stack2.widget(idx).currentItem().text() == 'Изменить длину':
            curveChangeLengthWidget = self.__curveChangeLength(idx)
            self.Stack3.addWidget(curveChangeLengthWidget)
            self.Stack3.setCurrentWidget(curveChangeLengthWidget)
            self.Stack3.show()
            self.lineMover3.eventFilter('hide')

    # двигаем стрелкой влево
    def __handleLeftButton(self):
        self.Stack3.hide()
        self.transitionTempVerticalFirstLineTopLevel = None
        self.transitionTempVerticalSecondLineTopLevel = None
        #self.currentWidget.hide()
        if self.counter > 0 and self.counter < SUMMARY_LEN:
            self.counter = self.counter - 1
            self.transitionTempVerticalFirstLineTopLevel = round(get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185)
            self.transitionTempVerticalSecondLineTopLevel = round(get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185)
            self.updatedCounterSignal.emit(self.counter)
            #self.updatedCounterSignal.connect(self.__transitionChangeLength)
            self.__transitionChangeLength(self.counter).update()
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to left')
            self.lineMover2.eventFilter('to left')
            self.lineMover3.eventFilter('hide')
            if get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'transition':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: green;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'curve':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: red;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'straight':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: black;font-weight: bold;}")

    # двигаем стрелкой вправо
    def __handleRightButton(self):
        self.Stack3.hide()
        self.transitionTempVerticalFirstLineTopLevel = None
        self.transitionTempVerticalSecondLineTopLevel = None
        if self.counter >= 0 and self.counter < SUMMARY_LEN - 1:
            self.counter = self.counter + 1
            self.transitionTempVerticalFirstLineTopLevel = round(
                get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185)
            self.transitionTempVerticalSecondLineTopLevel = round(
                get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185)
            self.updatedCounterSignal.emit(self.counter)
            #self.updatedCounterSignal.connect(self.__transitionChangeLength)
            self.__transitionChangeLength(self.counter).update()
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter('to right')
            self.lineMover2.eventFilter('to right')
            self.lineMover3.eventFilter('hide')
            if get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'transition':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size:18px;color:green;font-weight:bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'curve':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: red;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'straight':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: black;font-weight: bold;}")

# __________________________transition_______________________
    # Переходная.Изменить_длину: сдвиг одной или обеих черт в любом направлении
    def __transitionChangeLength(self, idx: int):
        groupboxChangeLength = QGroupBox()
        changeLengthLayout = QHBoxLayout()
        groupboxChangeLength.setLayout(changeLengthLayout)
        self.spin_box1 = QSpinBox()
        self.spin_box1.setRange(-10000, 10000)
        self.spin_box1.setValue(get_csv_row(SUMMARYFILENAME, idx)[0][0] / 0.185)
        #self.spin_box1.sender = "__transitionChangeLength"
        #sender = "__transitionChangeLength"
        self.spin_box1.valueChanged.connect(self.__changeVerticaleLline1)
        font = self.spin_box1.font()
        font.setPointSize(16)
        self.spin_box1.setFont(font)
        self.spin_box2 = QSpinBox()
        self.spin_box2.setRange(-10000, 10000)
        self.spin_box2.setValue(get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185)
        self.spin_box2.valueChanged.connect(self.__changeVerticaleLline2)
        self.spin_box2.setFont(font)
        #self.transitionTempVerticalFirstLine = round(get_csv_row(SUMMARYFILENAME, idx)[0][0] / 0.185)
        #self.transitionTempVerticalSecondLine = round(get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185)
        self.displayLengthValue = QLabel(str(round(get_csv_row(SUMMARYFILENAME, idx)[0][2] / 0.185)))
        self.displayLengthValue.setStyleSheet("font-size: 18px;")
        title_label = QLabel("Длина")
        title_label.setStyleSheet("font-size: 18px;color: red;font-weight: bold;")
        changeLengthLayout.addWidget(self.spin_box1)
        changeLengthLayout.addStretch(1)
        changeLengthLayout.addWidget(title_label)
        changeLengthLayout.addStretch(1)
        changeLengthLayout.addWidget(self.displayLengthValue)
        changeLengthLayout.addStretch(1)
        changeLengthLayout.addWidget(self.spin_box2)
        return groupboxChangeLength

    # Переходная. Разделить: посередине полос появляется третья разделяющая
    def __transitionDivideLength(self, idx: int):
        firstLineX = get_csv_row(SUMMARYFILENAME, idx)[0][0] / 0.185
        secondLineX = get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185
        middleX = firstLineX + (secondLineX - firstLineX) * 0.5
        self.lineMover3.eventFilter('divide', middleX)

    # Переходная. Сместить: обе черты двигаются одновременно
    def __transitionShift(self, idx: int):
        groupboxTransitionShift = QGroupBox()
        transitionShiftLayout = QHBoxLayout()
        groupboxTransitionShift.setLayout(transitionShiftLayout)
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-10000, 10000)
        self.spinBox.setValue(0)
        #sender = self.spinBox.senderSignalIndex()
        self.spinBox.valueChanged.connect(self.__changeBothVerticalLines)
        font = self.spinBox.font()
        font.setPointSize(16)
        self.spinBox.setFont(font)
        titleCoordVerticaleLline1 = QLabel("Левая граница")
        titleCoordVerticaleLline1.setStyleSheet("font-size: 18px;")
        titleCoordVerticaleLline2 = QLabel("Правая граница")
        titleCoordVerticaleLline2.setStyleSheet("font-size: 18px;")
        #titleShiftLeft = QLabel("Смещение влево на ")
        #titleShiftRight = QLabel("Смещение вправо на ")
        self.coordVerticaleLline1 = QLabel(str(round(get_csv_row(SUMMARYFILENAME, idx)[0][0] / 0.185)))
        self.coordVerticaleLline1.setStyleSheet("font: bold 18px;")
        self.coordVerticaleLline2 = QLabel(str(round(get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185)))
        self.coordVerticaleLline2.setStyleSheet("font: bold 18px;")
        title_label = QLabel("Смещение на ")
        title_label.setStyleSheet("font-size: 1px;color: red;font-weight: bold;")
        transitionShiftLayout.addWidget(self.spinBox)
        #if self.spinBox.value() > 0:
        #    transitionShiftLayout.addWidget(titleShiftRight)
        #elif self.spinBox.value() < 0:
        #    transitionShiftLayout.addWidget(titleShiftLeft)
        transitionShiftLayout.addStretch(1)
        transitionShiftLayout.addWidget(titleCoordVerticaleLline1)
        transitionShiftLayout.addWidget(self.coordVerticaleLline1)
        transitionShiftLayout.addStretch(1)
        transitionShiftLayout.addWidget(titleCoordVerticaleLline2)
        transitionShiftLayout.addWidget(self.coordVerticaleLline2)
        transitionShiftLayout.addStretch(1)
        return groupboxTransitionShift

# _____________________________curve________________________________
    # Круговая Кривая.Изменить Длину: симметричное сжатие-расширение диапазона
    def __curveChangeLength(self, idx):
        groupboxCurveShift = QGroupBox()
        сurveShiftLayout = QHBoxLayout()
        groupboxCurveShift.setLayout(сurveShiftLayout)
        length = round((get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185) - (get_csv_row(SUMMARYFILENAME, idx)[0][0]) / 0.185)
        self.spinBox = QSpinBox()
        self.spinBox.setRange(-length, 10000)
        self.spinBox.setValue(0)
        self.spinBox.valueChanged.connect(self.__handleSpinboxCurveChangeLength)
        font = self.spinBox.font()
        font.setPointSize(16)
        self.spinBox.setFont(font)
        titleCoordVerticaleLline1 = QLabel("Левая граница")
        titleCoordVerticaleLline1.setStyleSheet("font-size: 16px;")
        titleLength = QLabel("Длина")
        titleLength.setStyleSheet("font-size: 16px;")
        titleCoordVerticaleLline2 = QLabel("Правая граница")
        titleCoordVerticaleLline2.setStyleSheet("font-size: 16px;")
        self.coordVerticaleLline1 = QLabel(str(round(get_csv_row(SUMMARYFILENAME, idx)[0][0] / 0.185)))
        self.coordVerticaleLline1.setStyleSheet("font: bold 16px;")
        self.coordVerticaleLline2 = QLabel(str(round(get_csv_row(SUMMARYFILENAME, idx)[0][1] / 0.185)))
        self.coordVerticaleLline2.setStyleSheet("font: bold 16px;")
        self.curveChangeLengthValue = QLabel(str(length))
        self.curveChangeLengthValue.setStyleSheet("font: bold 16px;")
        сurveShiftLayout.addWidget(self.spinBox)
        сurveShiftLayout.addWidget(titleLength)
        сurveShiftLayout.addWidget(self.curveChangeLengthValue)
        сurveShiftLayout.addStretch(1)
        сurveShiftLayout.addWidget(titleCoordVerticaleLline1)
        сurveShiftLayout.addWidget(self.coordVerticaleLline1)
        сurveShiftLayout.addStretch(1)
        сurveShiftLayout.addWidget(titleCoordVerticaleLline2)
        сurveShiftLayout.addWidget(self.coordVerticaleLline2)
        сurveShiftLayout.addStretch(1)
        return groupboxCurveShift

    # Круговая Кривая. Изменить Радиус
    def __curveChangeRadius(self, idx):
        groupboxCurveChangeRadius = QGroupBox()
        groupboxCurveChangeRadiusLayout = QHBoxLayout()
        groupboxCurveChangeRadius.setLayout(groupboxCurveChangeRadiusLayout)
        spinBox = QSpinBox()
        spinBox.setRange(-1000, 1000)
        spinBox.setValue(0)
        spinBox.valueChanged.connect(self.__handleSpinboxCurveChangeRadius)
        self.currentRadius = QLabel(str(get_csv_row(SUMMARYFILENAME, idx)[0][3]))
        self.currentRadius.setStyleSheet("font: bold 18px;")
        font = spinBox.font()
        font.setPointSize(16)
        spinBox.setFont(font)
        title_label = QLabel("Радиус = ")
        title_label.setStyleSheet("font: 18px;")
        groupboxCurveChangeRadiusLayout.addWidget(spinBox)
        groupboxCurveChangeRadiusLayout.addStretch(1)
        groupboxCurveChangeRadiusLayout.addWidget(title_label)
        groupboxCurveChangeRadiusLayout.addWidget(self.currentRadius)
        groupboxCurveChangeRadiusLayout.addStretch(1)
        return groupboxCurveChangeRadius

    # КруговаяКривая 'ИзменитьДлину'
    def __handleSpinboxCurveChangeLength(self, value):
        length = round( (get_csv_row(SUMMARYFILENAME, self.counter)[0][1] - get_csv_row(SUMMARYFILENAME, self.counter)[0][0]) / 0.185, 1)
        self.vertical_model1.shiftLine(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185) - (value/2) )
        self.vertical_model2.shiftLine( round(get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185) + (value/2) )
        self.curveChangeLengthValue.setNum(round(length + value,1))
        self.coordVerticaleLline1.setNum( (round((get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185) - (value/2), 1) ))
        self.coordVerticaleLline2.setNum( (round((get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185) + (value/2), 1) ))


    # Круговая кривая 'изменить радиус'
    def __handleSpinboxCurveChangeRadius(self, value):
        updatedRadius = get_csv_row(SUMMARYFILENAME, self.counter)[0][3] + value
        self.currentRadius.setText(str(round(updatedRadius,2)))



    # Двигаем первую (левую) вертикальную черту + запускаем изменение в таблице + меняем данные в ячейке таблицы
    def __changeVerticaleLline1(self, value):
        self.vertical_model1.shiftLine(value)
        self.transitionTempVerticalFirstLineTopLevel = value
        result = round(self.transitionTempVerticalSecondLineTopLevel - value, 2)
        self.displayLengthValue.setText(str(result))
        #
        self.pandasModel.setData(self.pandasModel.index(1,1), result, Qt.EditRole) #self.pandasModel.index


    # Двигаем правую (вторую) вертикальную черту
    def __changeVerticaleLline2(self, value):
        self.vertical_model2.shiftLine(value)
        self.transitionTempVerticalSecondLineTopLevel = value
        result = value - self.transitionTempVerticalFirstLineTopLevel
        self.displayLengthValue.setText(str(result))

    # Двигаем обе черты в одну сторону (длина промежутка не меняется)
    def __changeBothVerticalLines(self, value):
        self.vertical_model1.shiftLine(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185) + value)
        self.vertical_model2.shiftLine(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185) + value)
        self.coordVerticaleLline1.setText(str(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][0] / 0.185) + value))
        self.coordVerticaleLline2.setText(str(round(get_csv_row(SUMMARYFILENAME, self.counter)[0][1] / 0.185) + value))

    # def __onDataChanged(self, _from, _to):
    #     model = _from.model() # proxy model
    #     model.blockSignals(True)
    #     for index in self.view.selectionModel().selectedIndexes():
    #         model.setData(index, _from.data())
    #     model.blockSignals(False)
    #
    # def __changeDataTable(self, row, col, value):
    #     #index = self.proxyModel.mapFromSource(QtCore.QModelIndex())
    #     #row_count = self.proxyModel.rowCount(index)
    #     #original_value = self._original_table_data[row][col]
    #     index = self.proxyModel.index(row, col)
    #     self.proxyModel.setData(index, value)



    def resizeEvent(self, event):
        w = self.groupbox1.size().width()
        #x = (w - 182) / 2
        x = (w - 250) / 2
        self.button_to_left.move(x, -1)       
        #x = (w - 182) / 2 + 157
        x = (w - 182) / 2 + 220
        self.button_to_right.move(x, -1)


        
# model1 = VerticalLineModel(0)
# model2 = VerticalLineModel(0)
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     BW = BottomWidget(model1, model2)
#     BW.show()
#     sys.exit(app.exec())
