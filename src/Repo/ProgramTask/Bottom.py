
from PySide6.QtWidgets import (QWidget, QListWidget, QListWidgetItem,QTextEdit,QStackedWidget,QLabel,
                               QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QToolButton, QSpinBox)
from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView
from PySide6.QtGui import QFont, QIcon, QShortcut, Qt, QPen, QPainter, QImage, QPixmap, QColor, QShortcut
from PySide6.QtCore import Qt, QTimer, QObject, QDateTime, QCoreApplication, Signal, QTimer, QSize, Signal, Slot
import sys
from ServiceInfo import *
#from ModelTable import *
from VerticalLine import VerticalLineModel1, VerticalLineModel2, MoveLineController



class BottomWidget(QWidget):
    updatedCounter = Signal(int)
    def __init__(self, model1:VerticalLineModel1, model2:VerticalLineModel2):
        super().__init__()
        #
        self.counter = 0
        #self.updatedCounter.emit(self.counter)
        #self.updatedCounter.connect(self.__transition_change_length)
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
        #self.groupbox1.setFocusPolicy(Qt.NoFocus)
        #
        self.vertical_model1 = model1
        self.vertical_model2 = model2
        self.lineMover1 = MoveLineController(0, self.vertical_model1, self.vertical_model2)
        #self.installEventFilter(self.lineMover1)
        self.lineMover2 = MoveLineController(0, self.vertical_model1, self.vertical_model2)
        #self.installEventFilter(self.lineMover2)
        #
        self.Stack1 = QStackedWidget()
        self.fill_first_stackwidget(SUMMARYFILENAME)
        self.vbox_groupbox1.addWidget(self.Stack1)
        #
        self.Stack2 = QStackedWidget()
        self.Stack2.setMaximumHeight(110)
        self.fill_second_stackwidget(SUMMARYFILENAME)
        self.vbox_groupbox2.addWidget(self.Stack2)
        self.vbox_groupbox2.addStretch(2)
        self.selected_function_shortcut = QShortcut(Qt.Key_Return, self)             # выбор клавиший 'enter'
        self.selected_function_shortcut.activated.connect(lambda: self.__selected_reconstruction_function())
        #
        self.Stack3 = QStackedWidget()
        self.fill_third_stackwidget()
        self.vbox_groupbox2.addWidget(self.Stack3)
        self.Stack3.hide()
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
        self.button_to_left.clicked.connect(self.handle_left_button)  
        self.button_to_right = QToolButton(self.groupbox1) 
        self.button_to_right.setIcon(QIcon("Data/right-arrow.png"))
        self.button_to_right.setIconSize(QSize(22, 22))
        self.button_to_right.setFixedSize(QSize(25, 25))
        self.button_to_right.clicked.connect(self.handle_right_button)  
        #
        self.textEdit = QTextEdit()    #QWidget()
        #self.right_text_field.ad
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

    def fill_first_stackwidget(self, summary: str):
        for i in range(0, SUMMARY_LEN, 1):
            self.table = MyTable(PandasModel, fill_first_stackwidget(summary, i))
            #self.table.setFocusPolicy(Qt.NoFocus)
            self.Stack1.addWidget(self.table)
            
    # заполнение данными второго блока "функции переустройства"
    # запускается сразу
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


    def fill_third_stackwidget(self):
        funcs_list = [['Изменить Lпк', 'Длина'], ['Разделить ПК', ''], ['Сместить ПК', 'Положение'],
                     ['Исключить ПК', ''],['Изменить радиус', 'Радиус'], ['Изменить длину', 'Длина']]
        for func in funcs_list:
            if func == ['Изменить Lпк', 'Длина']:
                widget = self.__transition_change_length(self.counter)   # func[1],
                self.Stack3.addWidget(widget)
            else:
                widget = self.input_data_widget(func[1])
                self.Stack3.addWidget(widget)
                

    def __selected_reconstruction_function(self):
        if self.Stack2.widget(self.counter).currentItem().text() == 'Изменить Lпк':
            #print('Изменить Lпк')
            #print(self.counter) #get_csv_row(SUMMARYFILENAME, self.counter)[0][0]) # / 0.85)
            self.Stack3.setCurrentIndex(0)
            self.Stack3.show()
        elif self.Stack2.widget(self.counter).currentItem().text() == 'Разделить ПК':
            self.Stack3.hide()
            #print('Разделить Lпк')
        elif self.Stack2.widget(self.counter).currentItem().text() == 'Сместить ПК':
            #print('Сместить Lпк')
            self.Stack3.setCurrentIndex(2)
            self.Stack3.show()
        elif self.Stack2.widget(self.counter).currentItem().text() == 'Исключить ПК':
            self.Stack3.hide()
            #print('Изменить Lпк')
        elif self.Stack2.widget(self.counter).currentItem().text() == 'Изменить радиус':
            self.Stack3.setCurrentIndex(4)
            self.Stack3.show()
        elif self.Stack2.widget(self.counter).currentItem().text() == 'Изменить длину':
            self.Stack3.setCurrentIndex(5)
            self.Stack3.show()

    def handle_left_button(self):
        self.Stack3.hide()
        if self.counter > 0 and self.counter < SUMMARY_LEN:
            self.counter = self.counter - 1
            self.updatedCounter.emit(self.counter)
            self.updatedCounter.connect(self.__transition_change_length)
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter1('to left')
            self.lineMover2.eventFilter1('to left')
            if get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'transition':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: green;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'curve':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: red;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'straight':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: black;font-weight: bold;}")


    def handle_right_button(self):
        self.Stack3.hide()
        if self.counter >= 0 and self.counter < SUMMARY_LEN - 1:
            self.counter = self.counter + 1
            #print(self.counter)
            self.updatedCounter.emit(self.counter)
            self.updatedCounter.connect(self.__transition_change_length)
            self.Stack1.setCurrentIndex(self.counter)
            self.Stack2.setCurrentIndex(self.counter)
            self.lineMover1.eventFilter1('to right')
            self.lineMover2.eventFilter1('to right')
            if get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'transition':
                self.groupbox1.setTitle("Переходная кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size:18px;color:green;font-weight:bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'curve':
                self.groupbox1.setTitle("Круговая кривая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: red;font-weight: bold;}")
            elif get_csv_row(SUMMARYFILENAME, self.counter)[0][-1] == 'straight':
                self.groupbox1.setTitle("Прямая")
                self.groupbox1.setStyleSheet("QGroupBox{font-size: 18px;color: black;font-weight: bold;}")

    # Интерфейс для Переходная_Изменить_длину
    #@Slot(int)
    def __transition_change_length(self, idx: int):
        groupbox_input = QGroupBox()
        groupbox_input_layout = QHBoxLayout()
        groupbox_input.setLayout(groupbox_input_layout)
        self.spin_box1 = QSpinBox()
        self.spin_box1.setRange(-1000, 1000)
        self.spin_box1.setValue(get_csv_row(SUMMARYFILENAME, idx)[0][0])
        font = self.spin_box1.font()
        font.setPointSize(16)
        self.spin_box1.setFont(font)
        self.spin_box2 = QSpinBox()
        self.spin_box2.setRange(-1000, 1000)
        self.spin_box2.setValue(get_csv_row(SUMMARYFILENAME, idx)[0][1])
        self.spin_box2.setFont(font)
        self.length_value = QLabel(str(get_csv_row(SUMMARYFILENAME, idx)[0][2]))
        self.length_value.setStyleSheet("font-size: 18px;")
        title_label = QLabel("Длина")
        title_label.setStyleSheet("font-size: 18px;color: red;font-weight: bold;")
        self.spin_box1.valueChanged.connect(self.__change_verticale_line1)
        self.spin_box2.valueChanged.connect(self.__change_verticale_line2)
        groupbox_input_layout.addWidget(self.spin_box1)
        groupbox_input_layout.addStretch(1)
        groupbox_input_layout.addWidget(title_label)
        groupbox_input_layout.addStretch(1)
        groupbox_input_layout.addWidget(self.length_value)
        groupbox_input_layout.addStretch(1)
        groupbox_input_layout.addWidget(self.spin_box2)
        return groupbox_input


    # интерфейс для всех кроме Переходная_Изменить_длину, по сути заглушка
    def input_data_widget(self, title:str):
        groupbox_input = QGroupBox()
        groupbox_input_layout = QHBoxLayout()
        groupbox_input.setLayout(groupbox_input_layout)
        spin_box = QSpinBox()
        spin_box.setRange(-1000,1000)
        spin_box.setValue(0)
        font = spin_box.font()
        font.setPointSize(16)
        spin_box.setFont(font)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px;color: red;font-weight: bold;")
        #spin_box.valueChanged.connect(self.__update_speed_spinbox_input_data_widget)
        groupbox_input_layout.addWidget(spin_box)
        groupbox_input_layout.addWidget(QLabel(str(self.counter)))
        groupbox_input_layout.addWidget(title_label)
        return groupbox_input


    def __change_verticale_line1(self, value):
        self.vertical_model1.shiftLine(value + (first_points[self.counter] / 0.185))
        self.length_value.setText(str(get_csv_row(SUMMARYFILENAME, self.counter)[0][2] - 1))
        print(value, first_points[self.counter], (first_points[self.counter + 1] / 0.185))

    def __change_verticale_line2(self, value):
        self.vertical_model2.shiftLine(value + (second_points[self.counter] / 0.185))
        self.length_value.setText(str(get_csv_row(SUMMARYFILENAME, self.counter)[0][2] + 1))
        print(value, second_points[self.counter], (second_points[self.counter] / 0.185))

    def resizeEvent(self, event):
        w = self.groupbox1.size().width()
        #x = (w - 182) / 2
        x = (w - 250) / 2
        self.button_to_left.move(x, -1)       
        #x = (w - 182) / 2 + 157
        x = (w - 182) / 2 + 220
        self.button_to_right.move(x, -1)


        
model1 = VerticalLineModel1(0)
model2 = VerticalLineModel2(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    BW = BottomWidget(model1, model2)
    BW.show()
    sys.exit(app.exec())
