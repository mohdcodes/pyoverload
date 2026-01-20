"""

core.py

------

cover  overload resolution engine.

This module defines the OverloadedFunction class, which stores multiple implementations of a callable and resolves the correct one at runetime based on function signatures

"""

from __future__ import annotations
import inspect
from typing import Callable, List, Tuple
from .utils import select_best_match
from .errors import NoMatchingOverloadError
from .cache import OverloadCache


class OverloadedFunction:
    """
    
    A callable object that holds multiple implementations of a function and resolves the correct one at runtime using argument matching.

    This class is framework-agnostic and does not depend on decorators, metaclasses, or frame inspection.
    
    """

    def __init__(self, name:str | None = None):
        """
        Initializse an overloaded funtion container.

        Args:
            name (str | None): Optional logical  name of the function.
        """

        self.name = name
        self.implementations:List[Tuple[inspect.signature, Callable]] = []
        self._cache = OverloadCache()

    #Register
    def register(self, func: Callable) -> "OverloadedFunction":
        """
        Decorator-style registration:
        @f.register
        def f(...):
        """
        self._register_impl(func)
        return self

    def _register_impl(self, func: Callable) -> None:
        if not callable(func):
            raise TypeError("Only callables can be registered")

        signature = inspect.signature(func)
        self.implementations.append((signature, func))

    #Dispatch
    def resolve(self, *args, **kwargs) -> Callable:
        """
        Resolve the best matching implementation for the given arguments.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Callable: The resolved function implementation.

        Raises:
            NoMatchingOverloadError: if no matching overload is found.
        """
        # Check cache first
        cached = self._cache.get(self.name, args, kwargs)
        if cached:
            return cached

        for sig, func in self.implementations:
            try:
                # Bind arguments partially; allows skipping self/cls for instance/class methods
                bound = sig.bind_partial(*args, **kwargs)
            except TypeError:
                continue

            match = True
            parameters = list(sig.parameters.keys())
            # Skip type checking for self/cls (first parameters)
            skip_first = parameters and parameters[0] in ("self", "cls")

            for i, (name, value) in enumerate(bound.arguments.items()):
                if skip_first and i == 0:
                    continue  # skip type check for self or cls

                param = sig.parameters[name]
                if param.annotation is inspect._empty:
                    continue

                if not isinstance(value, param.annotation):
                    match = False
                    break

            if match:
                # Cache the match for future calls
                self._cache.set(self.name, args, kwargs, func)
                return func

        # If no match found, raise error
        raise NoMatchingOverloadError(self.name, args, kwargs)


    #Invocation
    def __call__(self, *args, **kwargs):
        """
        Call the resolved function implementation
        This makes OverloadedFucntion itself callable
        """
        func  = self.resolve(*args, **kwargs)
        return func(*args, **kwargs)
    
    # Intorsepction helper
    def implementation(self)-> List[Callable]:
        """
        Returns all registered implementation

        Returns:
            List[Callable]: Registered functions
        """
        return [func for _, func in self.implementations]
    
    def signatures(self) -> List[inspect.Signature]:
        """
        Returns all registered function signatures.

        Returns:
            List[inspect.Signature]: Registered function signatures
        """
        return [signature for signature, _ in self.implementations]
    


    def __get__(self, instance, owner):
        """
        Descriptor protocol to support instance methods and classmethods.
        
        When called with instance=<class>, it means we're being accessed through
        @classmethod, and we should return a bound method with the class.
        When called with instance=<object>, it means we're being accessed as
        an instance method, and we should return a bound method with the instance.
        """
        if not self.implementations:
            return self
            
        sig, _ = self.implementations[0]
        first_param_name = list(sig.parameters.keys())[0] if sig.parameters else None

        # If instance is a class, bind it (handles both @classmethod and direct class access)
        if isinstance(instance, type):
            def bound(*args, **kwargs):
                return self(instance, *args, **kwargs)
            return bound

        # If instance is an object instance, bind it for instance methods
        if instance is not None and first_param_name == "self":
            def bound(*args, **kwargs):
                return self(instance, *args, **kwargs)
            return bound

        # Otherwise return dispatcher itself (for static methods or direct access)
        return self

