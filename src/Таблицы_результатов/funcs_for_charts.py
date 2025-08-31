import random
import math


def func1(start, stop):
    final=[]
    for i in range(start, stop, 1):
        result=[]
        result.append(i)
        result.append(math.sin(i))
        final.append(result)
    return final
        
def func2(start, stop):
    final=[]
    for i in range(start, stop, 1):
        result=[]
        result.append(i)
        result.append(math.sin(i) * 0.02)
        final.append(result)
    return final

def func3(start, stop):
    final=[]
    for i in range(start, stop, 1):
        result=[]
        result.append(i)
        result.append(math.sin(i) * (math.sin(i) ** (-1)))
        final.append(result)
    return final

def func4(start, stop):
    final=[]
    for i in range(start, stop, 1):
        result=[]
        result.append(i)
        result.append(math.sin(i) ** (-1) + 5)
        final.append(result)
    return final

def func5(start, stop):
    final=[]
    for i in range(start, stop, 1):
        result=[]
        result.append(i)
        result.append(math.sin(i) ** (-3))
        final.append(result)
    return final
