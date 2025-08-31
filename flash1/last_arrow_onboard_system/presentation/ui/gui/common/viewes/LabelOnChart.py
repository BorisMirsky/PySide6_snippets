from PySide6.QtWidgets import QWidget, QLabel



class LabelOnParent(QLabel):
    def __init__(self, title, parent):
        super(LabelOnParent, self).__init__(title, parent)
        self.move(1600,20)


class LabelOnParent1(QLabel):
    def __init__(self, title, parent):
        super(LabelOnParent1, self).__init__(title, parent)
        self.move(1000,10)

class LabelOnParent2(QLabel):
    def __init__(self, title, x1, y1, x2, y2, parent):
        super(LabelOnParent2, self).__init__(title, parent)
        self.move(x1, y1)
        self.resize(x2, y2)