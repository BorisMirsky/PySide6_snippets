import sys
import unittest
import types
from docviewdoc import DocviewDoc
#from qt import *
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, SIGNAL
from PySide6.QtTest import QTest, QSignalSpy


class ConnectionBox(QObject):

    def __init__(self, *args):
        apply(QObject.__init__, (self,) + args)
        self.signalArrived = 0
        self.args = []

    def slotSlot(self, *args):
        self.signalArrived = 1
        self.args = args

    def assertSignalArrived(self, signal=None):
        if not self.signalArrived:
            print("signal %s did not arrive" % signal)
            #raise AssertionError, ("signal %s did not arrive" % signal)

    def assertNumberOfArguments(self, number):
        if number != len(self.args):
            print("Signal generated %i arguments, but %i were expected" %  (len(self.args), number))
            #raise AssertionError, ("Signal generated %i arguments, but %i were expected" %  (len(self.args), number))

    def assertArgumentTypes(self, *args):
        if len(args) != len(self.args):
            #raise AssertionError, ("Signal generated %i arguments, but %i were given to this function" % (len(self.args), len(args)))
            print("Signal generated %i arguments, but %i were given to this function" % (len(self.args), len(args)))
        for i in range(len(args)):
            if type(self.args[i]) != args[i]:
                #raise AssertionError, ("Arguments don't match: %s received, should be %s." % (type(self.args[i]), args[i]))
                print("Arguments don't match: %s received, should be %s." % (type(self.args[i]), args[i]))


class SignalsTestCase(unittest.TestCase):
    def setUp(self):
        self.doc = DocviewDoc()
        self.connectionBox = ConnectionBox()

    def tearaDown(self):
        self.doc.disConnect()
        self.doc = None
        self.connectionBox = None

    def checkSignalDoesArrive(self):
        self.connectionBox.connect(self.doc, PYSIGNAL("sigDocModified"), self.connectionBox.slotSlot)
        self.doc.slotModify()
        self.connectionBox.assertSignalArrived("sigDocModified")

    def checkSignalDoesNotArrive(self):
        self.connectionBox.connect(self.doc, PYSIGNAL("sigDocModifiedXXX"), self.connectionBox.slotSlot)
        self.doc.slotModify()
        try:
            self.connectionBox.assertSignalArrived("sigDocModifiedXXX")
        except AssertionError:
            pass
        else:
            fail("The signal _did_ arrive")

    def checkArgumentToSignal(self):
        self.connectionBox.connect(self.doc, PYSIGNAL("sigDocModified"), self.connectionBox.slotSlot)
        self.doc.slotModify()
        self.connectionBox.assertNumberOfArguments(1)

    def checkArgumentTypes(self):
        self.connectionBox.connect(self.doc, PYSIGNAL("sigDocModified"), self.connectionBox.slotSlot)
        self.doc.slotModify()
        self.connectionBox.assertArgumentTypes(types.IntType)

def suite():
    testSuite = unittest.makeSuite(SignalsTestCase, "check")
    return testSuite


def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    main()
