
class myClass():
    def __init__(self, arg1, arg2, *args, **kwargs):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        if 'karg1' in kwargs.keys():
            self.karg1 = kwargs['karg1']
            self.processKarg1
        if 'hhh' in args:
            self.hhh = 'hhh'

    def method1(self):
        print(self.arg1)

    def processKarg1(self):
        print(self.karg1)

    def printHHH(self):
        print(self.hhh)

instance = myClass('q', 'w', 'asd', 'hhh', karg1=66)
#instance.method1()
#instance.processKarg1()
instance.printHHH()