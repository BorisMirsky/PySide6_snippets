#Неизвестно, какие именно аргументы придут, поэтому надо написать фильтрующее условие


def func(**kargs):
    if 'x' in kargs.keys():
        print(kargs['x'])
    if 'zzz' in kargs.keys():
        print(kargs['zzz'])
    if 'n' in kargs.keys():
        print(kargs['n'] * 6)
        

func(n=4, x='aaa', a=22)
