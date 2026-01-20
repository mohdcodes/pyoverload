"""
typing.py
---------

Utilities for runtime type matching used by pyoverload.
"""

from __future__ import annotations

import typing
from typing import Any, get_origin, get_args


def is_any(annotation) -> bool:
    return annotation is Any


def is_union(annotation) -> bool:
    return get_origin(annotation) is typing.Union


def is_optional(annotation) -> bool:
    return is_union(annotation) and type(None) in get_args(annotation)


def match_type(value, annotation) -> bool:
    """
    Check whether a runtime value matches a type annotation.

    Supports:
    - Any
    - Union / Optional
    - Built-in types
    - Generic containers (list[int], tuple[str], dict[str, int])
    """

    # No annotation → always match
    if annotation is inspect_empty(annotation):
        return True

    # Any → always match
    if is_any(annotation):
        return True

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Union / Optional
    if is_union(annotation):
        return any(match_type(value, arg) for arg in args)

    # Generic containers
    if origin in (list, tuple, set):
        if not isinstance(value, origin):
            return False
        if not args:
            return True
        return all(match_type(v, args[0]) for v in value)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if not args:
            return True
        key_t, val_t = args
        return all(
            match_type(k, key_t) and match_type(v, val_t)
            for k, v in value.items()
        )

    # Normal isinstance check
    try:
        return isinstance(value, annotation)
    except TypeError:
        return False


def inspect_empty(annotation) -> bool:
    """
    Check for missing annotation.
    """
    import inspect
    return annotation is inspect._empty
