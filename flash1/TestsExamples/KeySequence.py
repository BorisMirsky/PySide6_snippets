import json
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QDialog, QKeySequenceEdit, QApplication
from PySide6.QtCore import Signal as pyqtSignal
#from PySide6.QtGui import QKeySequenceEdit


hotkey.json = '{"slice_switching_left": "Ctrl+Left","slice_switching_right": "Ctrl+Right","hide_show_annotation": "Ctrl+X"}'

class KeySequenceEdit(QKeySequenceEdit):
    def keyPressEvent(self, event):
        super(KeySequenceEdit, self).keyPressEvent(event)
        seq_string = self.keySequence().toString(QKeySequence.NativeText)
        if seq_string:
            last_seq = seq_string.split(",")[-1].strip()
            self.setKeySequence(QKeySequence(last_seq))
            self.editingFinished.emit()


class HotKeysWidget(QDialog):
    """ Данный класс служит для добавлений горячих клавиш
    И обновлением их значений.
    """
    # Для обновления горячих клавиш в родительском классе
    setting_hotkeys = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(HotKeysWidget, self).__init__(parent)
        # self.setupUi(self)
        # self.setWindowModality(QtCore.Qt.WindowModal)
        # +++
        self._data = self.load_json()  # +++

        self.parent = parent
        self.tag_model = QStandardItemModel()
        self.output_data = {}
        self.vlay = QVBoxLayout(self)

        # Добавление горячих клавиш в виджет
        self.add_keysequence("Переключение слайсов влево", "slice_switching_left")
        self.add_keysequence("Переключение слайсов вправо", "slice_switching_right")
        self.add_keysequence("Полноэкранный режим", "full_windows")
        self.add_keysequence("Показать/Скрыт аннотацию", "hide_show_annotation")
        self.add_keysequence("Показать/Скрыт информативные окна", "hide_show_info_window")
        self.add_keysequence("Показать/Скрыт находку", "hide_show_nodules")

    def load_json(self):
        with open("hotkey.json", encoding="utf-8") as f:
            return json.load(f)

    def closeEvent(self, event):
        """ Функция сохраняет измененные значения горячих клавиш """

        data = self.load_json()
        result_data = {**data, **self.output_data}

        with open("hotkey.json", 'w', encoding='utf-8') as outfile:
            json.dump(result_data, outfile, indent=2, ensure_ascii=False, separators=(',', ': '))

        self.setting_hotkeys.emit(result_data)
        self.close()

    def add_keysequence(self, text, name_keysequence):
        """ Функция добавляет название для горячих клавиш
        и input для ввода значений горячих клавиш
        """
        self.name_keysequence = name_keysequence
        self._keysequenceedit = KeySequenceEdit(editingFinished=self.on_editingFinished)
        self._keysequenceedit.setObjectName(self.name_keysequence)
        self._keysequenceedit.setFixedWidth(100)

        label = QLabel(text=text)
        hlay = QHBoxLayout()
        hlay.addWidget(label)
        hlay.addWidget(self._keysequenceedit)

        # +++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        val = self._data.get(self._keysequenceedit.objectName())
        if val: self._keysequenceedit.setKeySequence(val)
        # +++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        self.vlay.addLayout(hlay)

    def on_editingFinished(self):
        """ Функция обновляет значения горячих клавиш """

        obj = self.sender()
        sequence = obj.keySequence()
        seq_string = sequence.toString(QKeySequence.NativeText)
        flag = self.check_duplicate(seq_string, obj.objectName())
        if flag:
            self.output_data.update({obj.objectName(): seq_string})
        else:
            print("Дубликат")

    def check_duplicate(self, seq_string, name_obj):
        """ Проверяет на наличие дубликаты в основном словаре,
        при его обновлении
        """
        data = self.load_json()
        for key, value in data.items():
            if key != name_obj:
                if value == seq_string:
                    return False
        return True


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = HotKeysWidget()
    w.show()
    sys.exit(app.exec())