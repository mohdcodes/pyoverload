from pyoverload.decorators import overload


class Calculator:

    @overload
    def add(self, a, b):
        return a + b

    @overload
    def add(self, a, b, c):
        return a + b + c


calc = Calculator()

print(calc.add(1, 2))
print(calc.add(1, 2, 3))

print("Basic overload test passed")