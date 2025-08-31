from PySide6.QtWidgets import QGridLayout, QWidget, QLabel

class MachineStatusPanel(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('Рабочий стрелограф'), 0, 0, 1, 4)
        layout.addWidget(QLabel('-3.4'), 0, 4, 1, 1)
        layout.addWidget(QLabel('-4.5'), 0, 5, 1, 1)
        layout.addWidget(QLabel('Проект'), 0, 6, 1, 2)
        layout.addWidget(QLabel('Сдвиги'), 0, 8, 1, 1)
        layout.addWidget(QLabel('-4.7'), 1, 8, 1, 1)
        layout.addWidget(QLabel('Рабочий уровень'), 0, 9, 1, 3)
        layout.addWidget(QLabel('Возвышение'), 1, 9, 1, 3)
        layout.addWidget(QLabel('0.2'), 0, 12, 1, 1)
        layout.addWidget(QLabel('0.0'), 1, 12, 1, 1)
        layout.addWidget(QLabel('Профиль'), 0, 13, 1, 4)
        layout.addWidget(QLabel('Левый'), 1, 13, 1, 2)
        layout.addWidget(QLabel('2.6'), 1, 15, 1, 1)
        layout.addWidget(QLabel('2.8'), 1, 16, 1, 1)
        layout.addWidget(QLabel('1.6'), 0, 17, 1, 2)
        layout.addWidget(QLabel('Правый'), 1, 17, 1, 2)
        layout.addWidget(QLabel('Подъёмки'), 0, 19, 1, 2)
        layout.addWidget(QLabel('10.7'), 1, 19, 1, 2)



if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = MachineStatusPanel()
    #w = MiddlePanelClass()
    w.show()
    sys.exit(app.exec())






#lbl_css_1 = ("font-weight: bold;font-size: 20px;color: yellow;background-color:blue;") #setContentsMargins:5,5,5,5")
#lbl_css_2 = ("font-weight: bold;font-size: 20px;color: white;background-color:black")
#lbl_css = ("font-weight: bold;font-size: 18px;color: black;")
#groupbox_css = ("border: 2px solid gray; border-radius: 3px; ")


#PEREGON = "АНЖЕРСКАЯ-ТАЙГА"
#PUT = "1"


#def current_time():
#    current_time = QDateTime.currentDateTime()
#    formatted_time = current_time.toString('hh:mm:ss')
#    return formatted_time


#class MiddlePanelClass(QWidget):
#    def __init__(self):
#        super().__init__()
#        self.init_UI()

#    def init_UI(self):
#        lbl_1_1 = QLabel("Рабочий стрелограф")
#        lbl_1_1.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#7CFA4C;")
#        lbl_1_2 = QLabel("-3.4")
#        lbl_1_2.setContentsMargins(5,5,5,20)
#        lbl_1_2.setStyleSheet(lbl_css_2)
#        lbl_1_3 = QLabel("-4.5")
#        lbl_1_3.setContentsMargins(15, 5, 5, 5)
#        lbl_1_3.setStyleSheet(lbl_css_1)
#        lbl_1_4 = QLabel("Проект")
#        lbl_1_4.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#7CFA4C;")
#        lbl_1_5 = QLabel("Сдвиги")
#        lbl_1_5.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#7CFA4C;")
#        lbl_1_6 = QLabel("Рабочий уровень")
#        lbl_1_6.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#F397D1;")
#        lbl_1_7 = QLabel("0.2")
#        lbl_1_7.setContentsMargins(15, 5, 5, 5)
#        lbl_1_7.setStyleSheet(lbl_css_2)
#        lbl_1_8 = QLabel("Профиль")
#        lbl_1_8.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#F2F91E;")
#        lbl_1_8.setAlignment(Qt.AlignHCenter)
#        lbl_1_9 = QLabel("1.6")
#        lbl_1_9.setContentsMargins(15, 5, 5, 5)
#        lbl_1_9.setStyleSheet(lbl_css_1)
#        lbl_1_10 = QLabel("Подъёмки")
#        lbl_1_10.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#97F0F3;")
#        #
#        lbl_empty = QLabel(" ")
#        lbl_empty.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#7CFA4C;")
#        lbl_2_1 = QLabel("-4.7")
#        lbl_2_1.setStyleSheet(lbl_css_1)
#        lbl_2_1.setContentsMargins(15, 5, 5, 5)
#        lbl_2_2 = QLabel("Возвышение")
#        lbl_2_2.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#F397D1;")
#        lbl_2_3 = QLabel("0.0")
#        lbl_2_3.setStyleSheet(lbl_css_1)
#        lbl_2_3.setContentsMargins(15, 5, 5, 5)
#        lbl_2_4 = QLabel("Левый")
#        lbl_2_4.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#F2F91E;")
#        lbl_2_5 = QLabel("2.6")
#        lbl_2_5.setStyleSheet(lbl_css_2)
#        lbl_2_5.setContentsMargins(15, 5, 5, 5)
#        lbl_2_6 = QLabel("2.8")
#        lbl_2_6.setStyleSheet(lbl_css_1)
#        lbl_2_6.setContentsMargins(15, 5, 5, 5)
#        lbl_2_7 = QLabel("Правый")
#        lbl_2_7.setStyleSheet("font-weight: bold;font-size: 20px;color: black;background-color:#97F0F3;")
#        lbl_2_8 = QLabel("10.7")
#        lbl_2_8.setContentsMargins(15, 5, 5, 5)
#        lbl_2_8.setStyleSheet(lbl_css_1)

#        hbox1 = QHBoxLayout()
#        hbox1.addWidget(lbl_1_1)
#        hbox1.addWidget(lbl_1_2)
#        hbox1.addWidget(lbl_1_3)
#        hbox1.addWidget(lbl_1_4)
#        hbox2 = QHBoxLayout()
#        hbox2.addWidget(lbl_2_4)
#        hbox2.addWidget(lbl_2_5)
#        hbox2.addWidget(lbl_2_6)
#        hbox2.addWidget(lbl_2_7)

#        GridLayout = QGridLayout()
#        GridLayout.addLayout(hbox1, 0, 0)
#        GridLayout.addWidget(lbl_1_5, 0, 1)
#        GridLayout.addWidget(lbl_1_6, 0, 2)
#        GridLayout.addWidget(lbl_1_7, 0, 3)
#        GridLayout.addWidget(lbl_1_8, 0, 4)
#        GridLayout.addWidget(lbl_1_9, 0, 5)
#        GridLayout.addWidget(lbl_1_10, 0, 6)
#        GridLayout.addWidget(lbl_empty, 1, 0)
#        GridLayout.addWidget(lbl_2_1, 1, 1)
#        GridLayout.addWidget(lbl_2_2, 1, 2)
#        GridLayout.addWidget(lbl_2_3, 1, 3)
#        GridLayout.addLayout(hbox2, 1, 4)
#        GridLayout.addWidget(lbl_2_7, 1, 5)
#        GridLayout.addWidget(lbl_2_8, 1, 6)
#        self.setLayout(GridLayout)
#        return
