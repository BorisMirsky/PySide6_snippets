# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QApplication, QWidget, QAbstractSlider, QDial
from PySide6.QtCore import QObject, QEvent, Qt, QKeyCombination
from PySide6.QtGui import QKeyEvent, QShortcut, QKeySequence
import sys


"""
Мастер класс по отлову событий, три варианта:

1 CustomWidget 
1.1 Не понял, зачем в каждом методе дополнительно определять отдельный super(), достаточно только в __init()__, не?
1.2 Встроенные Qt-функции keyPressEvent & keyReleaseEvent слушают заданные клавиши.

2 KeyArrowsEventFilter
Кастомный класс фильтра событий, добавляется как аргумент в встроенный Qt'шный метод installEventFilter(),
который в свою очередь крепится через 'self' в методе __init__ внешнего класса. 
Смысл в том, что данная функциональность определяется отдельно в специальном классе.

3 DialWidget
Создаётся экземпляр класса QShortcut, который выступает как сигнал.
Предпочтительнее (?), чем eventFilter.




"""


class CustomWidget(QWidget):
    def __init__(self, parent: QWidget = None) ->None:
        super().__init__(parent)
        #self.installEventFilter(KeyArrowsEventFilter(self))                  # added
    def keyPressEvent(self, event: QKeyEvent) -> None:
        #super().keyPressEvent(event)
        if event.key() in (Qt.Key_Q, Qt.Key_W):
            print(f'Press: {event.key()}')
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        #super().keyPressEvent(event)              # keyReleaseEvent?
        if event.key() in (Qt.Key_A, Qt.Key_D):
            print(f'Release: {event.key()}')




class KeyArrowsEventFilter(QObject):
    def __init__(self, parent: QObject = None) ->None:
        super().__init__(parent)
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key_Z, Qt.Key_X):
                print(f'Catch press: {event.key()}')
        if event.type() == QEvent.Type.KeyRelease:
            if event.key() in (Qt.Key_C, Qt.Key_V):
                print(f'Catch release: {event.key()}')
        return False

##################################################################################################

class DialWidget(QDial):
    def __init__(self, parent: QWidget = None) ->None:
        super().__init__(parent)
        self.setSingleStep(1)
        self.setRange(-100, 100)
        #self.installEventFilter(KeyArrowsEventFilter(self))
        self.add_slider_shortcut = QShortcut(Qt.Key_T, self)
        self.sub_slider_shortcut = QShortcut(Qt.Key_G, self)
        self.reset_slider_shortcut = QShortcut(Qt.Key_B, self)
        self.add_slider_shortcut.activated.connect(
            lambda: self.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd))
        self.sub_slider_shortcut.activated.connect(
            lambda: self.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepSub))
        self.reset_slider_shortcut.activated.connect(lambda: self.setValue(0))




if __name__ == '__main__':
    app = QApplication(sys.argv)
    #window = DialWidget()    # CustomWidget() #
    window = CustomWidget()
    window.show()
    sys.exit(app.exec())
