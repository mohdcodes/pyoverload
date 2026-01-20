"""
cache.py
--------

Caching layer for overload resolution.

Caches resolved overloads based on:
- function name
- argument types
"""

from __future__ import annotations
from typing import Callable, Dict, Tuple


class OverloadCache:
    """
    Cache for resolved overloads.

    Key format:
        (function_name, arg_types, kwarg_types)
    """

    def __init__(self):
        self._cache: Dict[Tuple, Callable] = {}

    def _make_key(
        self,
        name: str,
        args: tuple,
        kwargs: dict
    ) -> Tuple:
        """
        Create a cache key from argument types.
        """
        arg_types = tuple(type(arg) for arg in args)
        kwarg_types = tuple(
            sorted((k, type(v)) for k, v in kwargs.items())
        )
        return (name, arg_types, kwarg_types)

    def get(
        self,
        name: str,
        args: tuple,
        kwargs: dict
    ) -> Callable | None:
        """
        Retrieve cached overload if present.
        """
        key = self._make_key(name, args, kwargs)
        return self._cache.get(key)

    def set(
        self,
        name: str,
        args: tuple,
        kwargs: dict,
        func: Callable
    ) -> None:
        """
        Store resolved overload in cache.
        """
        key = self._make_key(name, args, kwargs)
        self._cache[key] = func

    def clear(self) -> None:
        """
        Clear all cached entries.
        """
        self._cache.clear()
