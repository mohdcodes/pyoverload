# examples/types.py
from pyoverload.decorators import overload
from pyoverload.metaclass import OverloadMeta

print("===== TYPE HINT OVERLOAD TEST =====")

# Free function with type hints
@overload
def echo(value: int):
    print("→ echo(int) called")
    return value

@overload
def echo(value: str):
    print("→ echo(str) called")
    return value.upper()

print(echo(42))       # → echo(int) called\n42
print(echo("hello"))  # → echo(str) called\nHELLO

# Class with method overloads using type hints
class Printer(metaclass=OverloadMeta):

    @overload
    def print_value(self, value: int):
        print("→ Printer.print_value(int) called")
        return f"Number: {value}"

    @overload
    def print_value(self, value: str):
        print("→ Printer.print_value(str) called")
        return f"Text: {value}"

p = Printer()
print(p.print_value(10))       # → Printer.print_value(int) called\nNumber: 10
print(p.print_value("Python")) # → Printer.print_value(str) called\nText: Python
