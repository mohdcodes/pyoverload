# examples/classmethod.py
from pyoverload.decorators import overload
from pyoverload.metaclass import OverloadMeta

print("===== CLASS METHOD OVERLOAD =====")

class Greeter(metaclass=OverloadMeta):

    @overload
    @classmethod
    def greet(cls, name: str):
        print("→ classmethod greet(str) called")
        return f"Hello {name}"

    @overload
    @classmethod
    def greet(cls, name: int):
        print("→ classmethod greet(int) called")
        return f"Number {name}"

print(Greeter.greet("Alice"))  # → classmethod greet(str) called\nHello Alice
print(Greeter.greet(10))       # → classmethod greet(int) called\nNumber 10
