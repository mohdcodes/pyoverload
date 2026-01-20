"""
test_error_messages.py

Test that correct error messages are raised for invalid or unmatched overload calls.
"""

import pytest
from pyoverload.decorators import overload
from pyoverload.errors import NoMatchingOverloadError


def test_no_matching_overload_free_function():
    """Test that NoMatchingOverloadError is raised for free functions with unmatched arguments."""

    @overload
    def add(a: int, b: int):
        return a + b

    # Passing str instead of int
    with pytest.raises(NoMatchingOverloadError) as exc_info:
        add("hello", "world")

    # Check the message contains the function name
    assert "add" in str(exc_info.value)
    assert "args=('hello', 'world')" in str(exc_info.value)


def test_no_matching_overload_instance_method():
    """Test that NoMatchingOverloadError is raised for instance methods."""

    class Calculator:
        @overload
        def multiply(self, a: int, b: int):
            return a * b

    calc = Calculator()

    # Passing wrong types
    with pytest.raises(NoMatchingOverloadError) as exc_info:
        calc.multiply(2, "x")

    assert "multiply" in str(exc_info.value)
    # Error message includes the bound self instance
    assert "2, 'x'" in str(exc_info.value)


def test_no_matching_overload_class_method():
    """Test that NoMatchingOverloadError is raised for classmethods."""

    class Greeter:
        @overload
        @classmethod
        def greet(cls, name: str):
            return f"Hello {name}"

    # Passing wrong type
    with pytest.raises(NoMatchingOverloadError) as exc_info:
        Greeter.greet(123)  # int instead of str

    assert "greet" in str(exc_info.value)
    # Error message includes the bound class
    assert "123" in str(exc_info.value)


def test_no_matching_overload_static_method():
    """Test that NoMatchingOverloadError is raised for staticmethods."""

    class MathUtils:
        @overload
        @staticmethod
        def divide(a: int, b: int):
            return a / b

    with pytest.raises(NoMatchingOverloadError) as exc_info:
        MathUtils.divide("a", "b")

    assert "divide" in str(exc_info.value)
    assert "args=('a', 'b')" in str(exc_info.value)
