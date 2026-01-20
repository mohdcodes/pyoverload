"""
utils.py
--------

Utility helpers for overload resolution.

This module contains pure functions that:
- score how well a function signature matches arguments
- select the best overload
- detect ambiguity
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, List, Tuple

from .typing import match_type
from .errors import AmbiguousOverloadError


def score_parameter(value: Any, annotation: Any) -> int:
    """
    Score how well a value matches a single parameter annotation.

    Higher score = better match.
    """

    if annotation is inspect._empty:
        return 3

    if annotation is object:
        return 1

    # Exact type match
    if type(value) is annotation:
        return 10

    # Subclass match
    if isinstance(value, annotation):
        return 7

    # Union / Optional / Generics
    if match_type(value, annotation):
        return 6

    return -1  # mismatch


def score_signature(
    sig: inspect.Signature,
    args: tuple,
    kwargs: dict
) -> int:
    """
    Score how well a function signature matches the provided arguments.

    Returns:
        int: Total score or -1 if incompatible
    """

    try:
        bound = sig.bind(*args, **kwargs)
    except TypeError:
        return -1

    total_score = 0

    for name, value in bound.arguments.items():
        param = sig.parameters[name]
        score = score_parameter(value, param.annotation)

        if score < 0:
            return -1

        total_score += score

    return total_score


def select_best_match(
    name: str,
    implementations: List[Tuple[inspect.Signature, Callable]],
    args: tuple,
    kwargs: dict
) -> Callable:
    """
    Select the best matching overload implementation.

    Raises:
        AmbiguousOverloadError: if multiple matches have same best score
    """

    scored = []

    for sig, func in implementations:
        score = score_signature(sig, args, kwargs)
        if score >= 0:
            scored.append((score, func))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)

    best_score = scored[0][0]
    best_matches = [func for score, func in scored if score == best_score]

    if len(best_matches) > 1:
        raise AmbiguousOverloadError(name)

    return best_matches[0]
