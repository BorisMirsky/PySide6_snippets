# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QCoreApplication, QIdentityProxyModel, QObject, Qt
from typing import Optional, Any

class TranslatedHeadersTableModel(QIdentityProxyModel):
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        header = super().headerData(section, orientation, role)
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            header = QCoreApplication.translate('Measurement/control units', str(header))
        return header

