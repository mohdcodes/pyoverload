"""
pyoverload
==========

A runtime method/function overloading library for Python.

This package provides infrastructure for defining and resolving
multiple implementations of a function or method based on their
signatures.

Public API is intentionally minimal.
"""

from .decorators import overload
from .core import OverloadedFunction
from .errors import NoMatchingOverloadError

__all__ = [
    "overload",
    "OverloadedFunction",
    "NoMatchingOverloadError",
]