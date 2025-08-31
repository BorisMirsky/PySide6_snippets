from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
#from domain.rw_models.AbstractModels import AbstractReadWriteModel
import sys



class OneDialWidgetClass(QWidget):
    def __init__(self, min_range: int, max_range: int,
                 key_add: Qt, key_sub: Qt, key_reset: Qt,
                 controls: Dict[float, AbstractReadWriteModel],                                   #
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        self.__controls = controls                                                               #
        dial = QDial()
        dial.setSingleStep(1)
        dial.setRange(min_range, max_range)
        dial.add_slider_shortcut = QShortcut(key_add, self)
        dial.sub_slider_shortcut = QShortcut(key_sub, self)
        dial.reset_slider_shortcut = QShortcut(key_reset, self)
        dial.add_slider_shortcut.activated.connect(
            lambda: dial.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepAdd))
        dial.sub_slider_shortcut.activated.connect(
            lambda: dial.triggerAction(QAbstractSlider.SliderAction.SliderSingleStepSub))
        dial.reset_slider_shortcut.activated.connect(lambda: dial.setValue(0))
        dial.valueChanged.connect(self.value_changed)
        self.label = QLabel()
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(dial)
        self.setLayout(vbox)

    def controls(self) ->Dict[float, AbstractReadWriteModelModel]:                                       #
       return self.__controls

    def value_changed(self, value):
        self.label.setText(str(value))




class ThreeDialsWidgetClass(QWidget):
    def __init__(self, parent: QWidget = None) ->None:
        super().__init__(parent)
        label_valve_shift = QLabel("Вентиль \nсдвижки")
        label_lift_right_rail = QLabel("Подъёмка \nправого \nрельса")
        label_lift_left_rail = QLabel("Подъёмка \nлевого \nрельса")
        dial_valve_shift = OneDialWidgetClass(-100, 100, Qt.Key_T, Qt.Key_G, Qt.Key_B)
        dial_lift_right_rail = OneDialWidgetClass(-100, 100, Qt.Key_Y, Qt.Key_H, Qt.Key_N)
        dial_lift_left_rail = OneDialWidgetClass(-100, 100, Qt.Key_U, Qt.Key_J, Qt.Key_M)
        control_valve_shift = QLabel("'T' увеличение \n' 'G' уменьшение \n'B' сброс")
        control_lift_right_rail = QLabel("'Y' увеличение \n'H' уменьшение \n'N' сброс")
        control_lift_left_rail = QLabel("'U' увеличение \n'J' уменьшение \n'M' сброс")
        grid = QGridLayout()
        grid.addWidget(label_valve_shift, 0,0)
        grid.addWidget(label_lift_right_rail, 0, 1)
        grid.addWidget(label_lift_left_rail, 0, 2)
        grid.addWidget(dial_valve_shift, 1, 0)
        grid.addWidget(dial_lift_right_rail, 1, 1)
        grid.addWidget(dial_lift_left_rail, 1, 2)
        grid.addWidget(control_valve_shift, 2, 0)
        grid.addWidget(control_lift_right_rail, 2, 1)
        grid.addWidget(control_lift_left_rail, 2, 2)
        self.setLayout(grid)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ThreeDialsWidgetClass()
    window.show()
    sys.exit(app.exec())

