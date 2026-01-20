"""
metaclass.py
------------

Metaclass support for clean overload registration without frame inspection.
"""

from __future__ import annotations

from typing import Dict, List
from types import FunctionType

from .core import OverloadedFunction


class OverloadMeta(type):
    """
    Metaclass that collects overloaded methods and
    groups them into OverloadedFunction dispatchers.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        overloads: Dict[str, List[object]] = {}

        # Step 1: collect overloaded definitions
        for attr_name, obj in namespace.items():
            dispatcher = None
            wrapper = None
            
            # Check if it's a wrapped dispatcher (classmethod, staticmethod)
            if isinstance(obj, (classmethod, staticmethod)):
                wrapper = type(obj)
                if isinstance(obj.__func__, OverloadedFunction):
                    dispatcher = obj.__func__
            # Check if it's an unwrapped dispatcher
            elif isinstance(obj, OverloadedFunction):
                dispatcher = obj
            
            if dispatcher is not None:
                overloads.setdefault(attr_name, []).append((dispatcher, wrapper))

        # Step 2: merge overloads
        for method_name, dispatchers_info in overloads.items():
            merged = OverloadedFunction(name=method_name)
            wrapper = None

            for dispatcher, disp_wrapper in dispatchers_info:
                # Track the wrapper type (all should be the same)
                if disp_wrapper is not None:
                    wrapper = disp_wrapper
                    
                for sig, func in dispatcher.implementations:
                    merged.implementations.append((sig, func))

            # Re-wrap if necessary
            if wrapper is not None:
                namespace[method_name] = wrapper(merged)
            else:
                namespace[method_name] = merged

        return super().__new__(mcls, name, bases, namespace)
