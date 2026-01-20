"""
decorators.py
-------------

Public decorators for defining overloaded functions and methods.
"""

from __future__ import annotations
from typing import Callable
import inspect
from typing import Callable
from .core import OverloadedFunction

def overload(obj: Callable) -> OverloadedFunction:
    """
    Decorator to define overloaded functions or methods.

    Multiple functions with the same name decorated using @overload
    will be grouped into a single OverloadedFunction dispatcher.

    Supports:
    - free functions
    - instance methods
    - static methods
    - class methods
    """


    # 1. Detect staticmethod / classmethod

    is_static = isinstance(obj, staticmethod)
    is_class  = isinstance(obj, classmethod)

    if is_static or is_class:
        func = obj.__func__   # unwrap
    else:
        func = obj

    if not callable(func):
        raise TypeError("@overload can be applied only to callables")

    name = func.__name__


    # 2. Find defining namespace

    frame = inspect.currentframe().f_back
    namespace = frame.f_locals

    # 3. Create or reuse dispatcher
    existing = namespace.get(name)
    dispatcher = None
    
    # Check if we can reuse an existing dispatcher
    if existing is not None:
        # If it's wrapped in classmethod/staticmethod, unwrap it
        if isinstance(existing, (classmethod, staticmethod)):
            unwrapped = existing.__func__
            if isinstance(unwrapped, OverloadedFunction):
                dispatcher = unwrapped
        # If it's unwrapped
        elif isinstance(existing, OverloadedFunction):
            dispatcher = existing
    
    # Create new dispatcher if we couldn't reuse
    if dispatcher is None:
        dispatcher = OverloadedFunction(name=name)
        namespace[name] = dispatcher

    # 4. Register implementation
    dispatcher.register(func)

    # 5. Re-wrap correctly
    if is_static:
        return staticmethod(dispatcher)
    if is_class:
        return classmethod(dispatcher)

    return dispatcher
