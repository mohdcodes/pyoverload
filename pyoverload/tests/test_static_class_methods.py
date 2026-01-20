from pyoverload.decorators import overload

def test_static_class():
    class Calculator:
        @overload
        @staticmethod
        def mul(a: int, b: int):
            return a * b
        @overload
        @staticmethod
        def mul(a: int, b: int, c:int):
            return a * b * c

        @overload
        @classmethod
        def twice(cls, x: int):
            return x * 2

    calc = Calculator()
    print(calc.mul(2, 3))        # Should print 6
    print(calc.mul(2, 3, 4))     # Should print 24
    print(Calculator.twice(5))   # Should print 10



    print("Static and class method overload test passed")

if __name__ == "__main__":
    test_static_class()
