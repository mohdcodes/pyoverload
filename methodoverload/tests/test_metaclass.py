"""
Test metaclass-based method overloading.
"""

from methodoverload.decorators import overload
from methodoverload.metaclass import OverloadMeta


def test_free_function_overload():
    @overload
    def add(a: int, b: int):
        return a + b

    @overload
    def add(a: str, b: str):
        return a + b

    assert add(1, 2) == 3
    assert add("a", "b") == "ab"


def test_instance_method_overload():

    class Calculator(metaclass=OverloadMeta):

        @overload
        def add(self, a: int, b: int):
            return a + b

        @overload
        def add(self, a: str, b: str):
            return a + b

    calc = Calculator()

    assert calc.add(2, 3) == 5
    assert calc.add("x", "y") == "xy"


def test_mixed_types_resolution():

    class Tester(metaclass=OverloadMeta):

        @overload
        def echo(self, x: int):
            return "int"

        @overload
        def echo(self, x: object):
            return "object"

    t = Tester()

    assert t.echo(10) == "int"
    assert t.echo("hello") == "object"
