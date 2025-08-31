


class MyClass:
    def __init__(self):
        self.__private_var = 66


#class_instance = MyClass()
#print(class_instance._MyClass__private_var)

class MyClass1:
    def __init__(self, var):
        self.__private_var = var

    def display_private_var(self):
        print(f"__private_var: {self.__private_var}")  # Доступно внутри класса


class_instance = MyClass1(66)
class_instance.display_private_var()

