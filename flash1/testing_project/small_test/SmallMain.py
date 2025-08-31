from PySide6.QtWidgets import QComboBox, QWidget, QPushButton, QLabel, QHBoxLayout, QApplication



class MyWidget(QWidget):
    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.resize(400,200)
        self.n = 0
        self.lbl = QLabel("default", self)
        self.but = QPushButton("+ 1", self)
        self.cmb = QComboBox(self)
        self.cmb.addItems(["A", "B", "C"])
        lay_h_main = QHBoxLayout(self)
        lay_h_main.addWidget(self.cmb)
        lay_h_main.addWidget(self.but)
        lay_h_main.addWidget(self.lbl)
        self.setLayout(lay_h_main)
        self.cmb.currentIndexChanged.connect(
            lambda: self.lbl.setText(self.cmb.currentText()+f" {self.n}"))
        self.but.clicked.connect(self.update_label)

    def update_label(self):
        if self.isVisible():
            self.n += 1
            self.lbl.setText(self.cmb.currentText()+f" {self.n}")



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainw = MyWidget(None)
    app.setActiveWindow(mainw)
    mainw.show()
    sys.exit(app.exec())