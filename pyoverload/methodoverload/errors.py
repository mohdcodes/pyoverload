"""
errors.py
---------

Custom exception hierarchy for pyoverload.

All public-facing errors raised by the overload system
should inherit from OverloadError.
"""


class OverloadError(Exception):
    """
    Base class for all pyoverload-related errors.
    """
    pass


class NoMatchingOverloadError(OverloadError):
    """
    Raised when no registered overload matches the provided arguments.
    """

    def __init__(self, name: str, args, kwargs):
        super().__init__(
            f"No matching overload found for '{name}' "
            f"with args={args}, kwargs={kwargs}"
        )


class AmbiguousOverloadError(OverloadError):
    """
    Raised when multiple overloads match equally well.
    """

    def __init__(self, name: str):
        super().__init__(
            f"Ambiguous overload resolution for '{name}'"
        )


class InvalidOverloadSignatureError(OverloadError):
    """
    Raised when an overload has an invalid or unsupported signature.
    """
    pass
