# examples/staticmethod.py
from methodoverload.decorators import overload
from methodoverload.metaclass import OverloadMeta

print("===== STATIC METHOD OVERLOAD =====")

class Calculator(metaclass=OverloadMeta):

    @overload
    @staticmethod
    def multiply(a: int, b: int):
        print("→ static multiply(int,int) called")
        return a * b

    @overload
    @staticmethod
    def multiply(a: float, b: float):
        print("→ static multiply(float,float) called")
        return a * b

print(Calculator.multiply(2, 3))    # → static multiply(int,int) called\n6
print(Calculator.multiply(2.5, 4.0))# → static multiply(float,float) called\n10.0
