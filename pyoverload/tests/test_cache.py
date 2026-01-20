from methodoverload.decorators import overload
def test_basic_cache():
    class Calculator:
        @overload
        def add(self, a: int, b: int):
            return a + b

        @overload
        def add(self, a: str, b: str):
            return a + b

    calc = Calculator()

    assert calc.add(1, 2) == 3
    assert calc.add(1, 2) == 3  # ✅ should hit cache
    assert calc.add("foo", "bar") == "foobar"
    print("Cache overload test passed")

if __name__ == "__main__":
    test_basic_cache()

