from PySide6.QtWidgets import *

class Widget1(QWidget):
    def __init__(self, parent=None):
        super(Widget1, self).__init__(parent)
        self.setWindowTitle(self.tr("Calculation of plan, longitudinal and transverse profile"))
        label1 =  QLabel(self.tr("Driving"))
        label2 = QLabel(self.tr("Path"))
        label3 = QLabel(self.tr("Machine"))
        button1 = QPushButton(self.tr("Plan"))
        button2 = QPushButton(self.tr("Level"))
        button3 = QPushButton(self.tr("Profile"))
        vbox = QVBoxLayout()
        vbox.addWidget(label1)
        vbox.addWidget(label2)
        vbox.addWidget(label3)
        vbox.addWidget(button1)
        vbox.addWidget(button2)
        vbox.addWidget(button3)
        self.setLayout(vbox)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'qtbase', '_', path):
        app.installTranslator(translator)
    translator = QTranslator(app)
    path = ':/translations'
    if translator.load(QLocale.system(), 'example', '_', path):
        app.installTranslator(translator)
    w = Widget1()
    w.show()
    sys.exit(app.exec())


    
