# This Python file uses the following encoding: utf-8
from functools import wraps
from datetime import datetime

def execution_time_logger(callable):
    @wraps(callable)
    def wrapped(*args, **kwargs):
        start_time = datetime.now()
        result = callable(*args, **kwargs)
        finish_time = datetime.now()
        print(f'Execution of {callable}: [{(finish_time - start_time).total_seconds()}]')
        return result
    return wrapped


def creation_logger(cls):
    origin_init = cls.__init__
    def __init__(self, *args, **kwargs):
        print(f'[{cls}][create]')
        origin_init(self, *args, **kwargs)
    cls.__init__ = __init__
    return cls


def deletion_logger(cls):
    if hasattr(cls, '__del__'):
        origin_del = cls.__del__
        def __del__(self):
            print(f'[{cls}][delete]')
            origin_del(self)
    else:
        def __del__(self):
            print(f'[{cls}][delete]')

    cls.__del__ = __del__
    return cls


def lifetime_logger(cls):
    return creation_logger(deletion_logger(cls))
