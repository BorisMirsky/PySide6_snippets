from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Mid)
        #self.setLayout(QFormLayout(self))

        self.fonts = QFontComboBox(self)                               # !
        self.fonts.currentFontChanged.connect(self.handleFontChanged)  # !
        #self.layout().addRow('font:', self.fonts)                      # !

        for text in (
            'H\u2082SO\u2084 + Be',
            'Hello World !',
            ):
            for label in ('boundingRect', 'width', 'size'):
                field = QLabel(text, self)
                field.setStyleSheet('background-color: yellow')
                field.setAlignment(Qt.AlignCenter)
                #self.layout().addRow(label, field)

        #self.layout().addRow("TextEdit", QTextEdit("Hello QTextEdit"))

        self.handleFontChanged(self.font())

    def handleFontChanged(self, font):
#        print(f"font:  {font}")
        layout = self.layout()
        font.setPointSize(20)
        metrics = QFontMetrics(font)
        for index in range(1, layout.rowCount()):
            field = layout.itemAt(index, QFormLayout.FieldRole).widget()
            label = layout.itemAt(index, QFormLayout.LabelRole).widget()

            method = label.text().split(' ')[0]

            if type(field) == QLabel:
                text = field.text()
            elif type(field) == QTextEdit:
                text = field.toPlainText()

            if method == 'width':
                width = metrics.width(text)
            elif method == 'size':
                width = metrics.size(field.alignment(), text).width()
            elif method == 'boundingRect':
                width = metrics.boundingRect(text).width()
            else:
                width = metrics.width(text)

            field.setFixedWidth(width)
            field.setFont(font)
            label.setText('%s (%d):' % (method, width))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())