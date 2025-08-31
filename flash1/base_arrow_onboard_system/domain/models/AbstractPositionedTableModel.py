# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QAbstractTableModel
from ..dto.Travelling import LocationVector1D
from typing import List, Dict, Tuple
import pandas




class AbstractPositionedTableModel(QAbstractTableModel):
    """
    Так-с. Наша святая моделька. На неё надо молиться, холить и лелеять, и всячески уважать,
    потому что если она поломается -- накроектся вообще всё.

    Что нужно знать про модельку?....Ну, три важные вещи:
        * Моделька имеет фиксированный шаг. Как на запись, так и на чтение.
          Если моделька имеет шаг 0.625, а ты попробуешь дать ей 0.7, то
          любая имплементация обязана отработать, как будто это 0.625.
        * Есть разделение на 'value columns' и 'model columns'.
          + Value columns -- это именно колонки ИЗМЕРЕНИЙ. Это ВСЕ данные, кроме position.
            Типа вообще все. Все, кроме position. Их он не видит.
          + Model columns -- этот как value columns, но спереди (в нулевой индекс)
            прибита гвоздями-сотками колонка position. position -- float формара
            {0...N} * step_size, т.е. [0.625, 1.25, 1.875 ...]. Нужно для отображения
            графиков, таблиц и т.п.
        * DataFrame, лежащий в ядре модели -- не просто dataframe, а со
          строго определённой структурой (это на случай, если кто-то
          когда-то захочет реализовывать этот интефрейс).

          index-ом у этого dataframe является поле с именем position, содержащее шаги (step).
          step -- целое число от 0 до N (N -- число строк). Как это перевести в метры? Да
          очень просто -- умножаем каждый step на self.step().meters.
          Где взять step? Он лежит в любом файле (zip-архиве) с работой.
          Почему так сделано? Потому что нам, скорее всего, понадобится перерасчёт
          всего dataframe на другой шаг.
          Структура DataFrame может быть обновлена после обсуждаения
          с https://t.me/vpolyanski или https://t.me/qweeeerrttttyyy

          Строками нашего dataframe являются измерения. При этом эти строки соответствуют
          списку (по значениям и по позиции), возвращаемому вызовом valueColumns().

    Да. По-хорошему, эту модель нужно разделить на две: QObject (скажем, AbstractMeasurementsTable),
    работающий чисто с DataFrame и QAbstractTableModel, берущий этот AbstractMeasurementsTable,
    и дающий методы [rowCount, columnCount, headerData, и data] для отображения графика.

    И да, я сознательно иду в этом месте на нарушение SOLID (SRP) ради одной-единственной цели:
    максимальной оптимизации процесса отображения графиков и таблиц, ведь только сам класс
    может на 100% знать своё внутреннее устройство и максимально быстро отдавать нужные данные.

    Если нам когда-нибудь это понадобится, и мы сможем придумать эффективное разделение --
    не вопрос, разделяем модельки, радуемся жизни.
    """

    @staticmethod
    def roundedVector(self, step_size: LocationVector1D, vector: LocationVector1D) ->LocationVector1D:
        return LocationVector1D(round(vector.meters / step_size.meters) * step_size.meters)
    def step(self) ->LocationVector1D:
        pass
    def     dataframe(self) ->pandas.DataFrame:
        pass
    def reset(self, step: LocationVector1D, data: pandas.DataFrame):
        pass

    def minmaxPosition(self) ->Tuple[LocationVector1D, LocationVector1D]:
        pass
    def minmaxValueByColumn(self, column: str) ->Tuple[float, float]:
        pass
    def minmaxValueByIndex(self, index: int) ->Tuple[float, float]:
        pass
    def minmaxValueByColumnInRange(self, column: str, start_step: int, end_step: int) ->Tuple[float, float]:
        pass
    def minmaxValueByIndexInRange(self, index: int, start_step: int, end_step: int) ->Tuple[float, float]:
        pass

    def valueColumns(self) ->List[str]:
        pass
    def valueColumnCount(self) ->int:
        pass
    def valueColumnIndexAtName(self, name: str) ->int:
        pass
    def valueColumnNameAtIndex(self, index: int) ->str:
        pass

    def modelColumns(self) ->List[str]:
        return ['position'] + self.valueColumns()
    def modelColumnCount(self) ->int:
        return 1 + self.valueColumnCount()
    def modelColumnIndexAtName(self, name: str) ->int:
        return 0 if name == 'position' else 1 + self.valueColumnIndexAtName(name)
    def modelColumnNameAtIndex(self, index: int) ->str:
        return 'position' if index == 0 else self.valueColumnNameAtIndex(index - 1)

    def rowAtPosition(self, position: LocationVector1D) ->Dict[str, float]:
        pass
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        pass
    def setRowAtPosition(self, position: LocationVector1D, values: Dict[str, float]) ->None:
        pass


class AbstractPositionedReadTableModel(QAbstractTableModel):
    """    
    """
    @staticmethod
    def roundedVector(self, step_size: LocationVector1D, vector: LocationVector1D) ->LocationVector1D:
        return LocationVector1D(round(vector.meters / step_size.meters) * step_size.meters)
    
    def step(self) ->LocationVector1D:
        pass
    def dataframe(self) ->pandas.DataFrame:
        pass
    def reset(self, step: LocationVector1D, data: pandas.DataFrame):
        pass

    def minmaxPosition(self) ->Tuple[LocationVector1D, LocationVector1D]:
        pass
    def minmaxValueByColumn(self, column: str) ->Tuple[float, float]:
        pass
    def minmaxValueByIndex(self, index: int) ->Tuple[float, float]:
        pass
    def minmaxValueByColumnInRange(self, column: str, start_step: int, end_step: int) ->Tuple[float, float]:
        pass
    def minmaxValueByIndexInRange(self, index: int, start_step: int, end_step: int) ->Tuple[float, float]:
        pass

    def valueColumns(self) ->List[str]:
        pass
    def valueColumnCount(self) ->int:
        pass
    def valueColumnIndexAtName(self, name: str) ->int:
        pass
    def valueColumnNameAtIndex(self, index: int) ->str:
        pass

    def modelColumns(self) ->List[str]:
        return ['position'] + self.valueColumns()
    def modelColumnCount(self) ->int:
        return 1 + self.valueColumnCount()
    def modelColumnIndexAtName(self, name: str) ->int:
        return 0 if name == 'position' else 1 + self.valueColumnIndexAtName(name)
    def modelColumnNameAtIndex(self, index: int) ->str:
        return 'position' if index == 0 else self.valueColumnNameAtIndex(index - 1)

    def rowAtPosition(self, position: LocationVector1D) ->Dict[str, float]:
        pass
    def cellAtPosition(self, position: LocationVector1D, column: str) ->float:
        pass
