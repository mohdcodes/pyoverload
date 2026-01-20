# PyOverload Architecture

This document describes the high-level architecture and design of the PyOverload library.

## Overview

PyOverload implements **function and method overloading** for Python using type hints for dispatch resolution. The library consists of several key components that work together to enable this functionality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Code                                 │
│  @overload                                                   │
│  def func(x: int): ...                                       │
│                                                              │
│  @overload                                                   │
│  def func(x: str): ...                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              @overload Decorator                             │
│  - Extracts function info                                    │
│  - Creates/reuses OverloadedFunction                         │
│  - Registers implementation                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            OverloadedFunction                                │
│  - Stores multiple implementations                           │
│  - Implements __call__ for dispatch                          │
│  - Implements __get__ for descriptor protocol               │
│  - Manages resolution & caching                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────┬──────────────────────────────────────┐
│   resolve()          │  OverloadCache                        │
│  - Match arguments   │  - Cache resolved overloads          │
│  - Type checking     │  - Fast lookup by arg types          │
│  - Return function   │  - Cache invalidation                │
└──────────────────────┴──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         Matched Function Execution                           │
│  - Call resolved implementation                              │
│  - Return result                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. **@overload Decorator** (`decorators.py`)

The entry point for users. Handles:

- **Detection** of staticmethod/classmethod decorators
- **Namespace inspection** using frame introspection
- **Dispatcher creation or reuse** - creates an `OverloadedFunction` or finds existing one
- **Implementation registration** - adds the function to the dispatcher
- **Re-wrapping** - applies staticmethod/classmethod wrapper if needed

```python
def overload(obj: Callable) -> OverloadedFunction:
    # 1. Detect wrapper type
    is_static = isinstance(obj, staticmethod)
    is_class = isinstance(obj, classmethod)
    
    # 2. Extract raw function
    func = obj.__func__ if is_static or is_class else obj
    
    # 3. Get namespace
    frame = inspect.currentframe().f_back
    namespace = frame.f_locals
    
    # 4. Create or reuse dispatcher
    dispatcher = namespace.get(func.__name__)
    if not isinstance(dispatcher, OverloadedFunction):
        dispatcher = OverloadedFunction(name=func.__name__)
    
    # 5. Register implementation
    dispatcher.register(func)
    
    # 6. Re-wrap if needed
    return wrapper(dispatcher) if wrapper else dispatcher
```

### 2. **OverloadedFunction** (`core.py`)

The core dispatcher class. Key features:

- **Implementation storage** - maintains list of (signature, function) pairs
- **Type-based resolution** - matches arguments to type hints
- **Caching** - stores resolved overloads for performance
- **Descriptor protocol** - supports instance methods via `__get__`

**Key Methods:**

- `register(func)` - Add a new implementation
- `resolve(*args, **kwargs)` - Find matching implementation
- `__call__(*args, **kwargs)` - Execute resolved function
- `__get__(instance, owner)` - Support instance method binding

```python
class OverloadedFunction:
    def __init__(self, name: str | None = None):
        self.name = name
        self.implementations = []
        self._cache = OverloadCache()
    
    def resolve(self, *args, **kwargs):
        # Check cache first
        cached = self._cache.get(self.name, args, kwargs)
        if cached:
            return cached
        
        # Try each implementation
        for sig, func in self.implementations:
            if self._matches(sig, args, kwargs):
                self._cache.set(self.name, args, kwargs, func)
                return func
        
        # No match found
        raise NoMatchingOverloadError(self.name, args, kwargs)
```

### 3. **OverloadMeta Metaclass** (`metaclass.py`)

Simplifies overload registration in classes. Benefits:

- **Automatic merging** of multiple overload definitions
- **Support for wrapped methods** (classmethod, staticmethod)
- **Clean class definition** syntax

```python
class OverloadMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        overloads = {}
        
        # Collect overloaded definitions
        for attr_name, obj in namespace.items():
            # Handle wrapped dispatchers
            if isinstance(obj, (classmethod, staticmethod)):
                dispatcher = obj.__func__
                wrapper = type(obj)
            else:
                dispatcher = obj
                wrapper = None
            
            if isinstance(dispatcher, OverloadedFunction):
                overloads.setdefault(attr_name, []).append((dispatcher, wrapper))
        
        # Merge overloads
        for method_name, dispatchers_info in overloads.items():
            merged = OverloadedFunction(name=method_name)
            wrapper = None
            
            for dispatcher, disp_wrapper in dispatchers_info:
                if disp_wrapper:
                    wrapper = disp_wrapper
                for sig, func in dispatcher.implementations:
                    merged.implementations.append((sig, func))
            
            # Re-wrap if needed
            namespace[method_name] = wrapper(merged) if wrapper else merged
        
        return super().__new__(mcls, name, bases, namespace)
```

### 4. **OverloadCache** (`cache.py`)

Performance optimization through caching. 

- **Cache key** - (function_name, arg_types, kwarg_types)
- **Fast lookup** - O(1) for repeated calls with same argument types
- **Transparent** - no user interaction needed

```python
class OverloadCache:
    def _make_key(self, name, args, kwargs):
        arg_types = tuple(type(arg) for arg in args)
        kwarg_types = tuple(
            sorted((k, type(v)) for k, v in kwargs.items())
        )
        return (name, arg_types, kwarg_types)
```

### 5. **Error Handling** (`errors.py`)

Clear error messages when dispatch fails.

```python
class NoMatchingOverloadError(Exception):
    """Raised when no overload matches the given arguments."""
    pass
```

## Data Flow

### 1. **Definition Phase**

```
User defines overloaded function
    ↓
@overload decorator called
    ↓
Decorator creates OverloadedFunction
    ↓
Function registered with signature
    ↓
Dispatcher stored in namespace
    ↓
Next @overload call finds and reuses dispatcher
```

### 2. **Call Phase**

```
User calls overloaded function
    ↓
OverloadedFunction.__call__ invoked
    ↓
resolve() checks cache
    ↓
If cached, return cached function
    ↓
If not cached, iterate implementations
    ↓
For each implementation:
  - Try to bind arguments to signature
  - Check type hints against actual types
  - If match found, cache and return
    ↓
If no match, raise NoMatchingOverloadError
    ↓
Execute returned function with original arguments
```

## Type Resolution Strategy

The library uses **isinstance() checks** for type matching:

1. **Signature binding** - `sig.bind_partial(*args, **kwargs)`
2. **Type iteration** - Loop through parameters
3. **Type checking** - `isinstance(value, param.annotation)`
4. **First match wins** - Returns first matching overload

**Type hints supported:**
- Basic types: `int`, `str`, `float`, `bool`, `list`, `dict`, `tuple`
- Custom classes: Any user-defined class
- Built-in types: `type`, `object`, etc.

**Not supported:**
- Generic types: `List[int]`, `Dict[str, int]` (no generic checking)
- Union types: `Union[int, str]` (partial support)
- Optional: `Optional[int]` (use `int | None`)

## Descriptor Protocol

The `__get__` method enables method binding:

```python
def __get__(self, instance, owner):
    if isinstance(instance, type):
        # Called via class (classmethod case)
        return self
    
    if instance is not None:
        # Called via instance
        sig, _ = self.implementations[0]
        if sig.parameters[0] == "self":
            def bound(*args, **kwargs):
                return self(instance, *args, **kwargs)
            return bound
    
    return self
```

This allows:
- **Instance methods** - `self` automatically bound
- **Class methods** - Wrapped by `@classmethod` decorator
- **Static methods** - No binding needed

## Thread Safety

⚠️ **Current limitations:**
- Cache is not thread-safe
- Registration while using is not thread-safe

**For thread-safe use:**
- Define all overloads before multi-threaded access
- Don't register new overloads during execution

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|-----------------|-------|
| First call | O(n) | n = number of overloads, type checking required |
| Cached call | O(1) | Cache lookup |
| Resolution | O(n) | Linear search through implementations |
| Cache miss | O(n) | Must search from scratch |

**Optimization notes:**
- Caching provides ~10-100x speedup for repeated calls
- Order matters - first matching overload is used
- More specific types should come first

## Extension Points

### Custom Type Matching

Users can extend type matching by subclassing:

```python
class CustomOverloadedFunction(OverloadedFunction):
    def _matches_type(self, param_annotation, arg_value):
        # Custom type matching logic
        return custom_isinstance(arg_value, param_annotation)
```

### Custom Error Handling

```python
class CustomNoMatchError(NoMatchingOverloadError):
    def __init__(self, name, args, kwargs):
        super().__init__(name, args, kwargs)
        # Custom logging, metrics, etc.
```

## Design Decisions

### 1. **Type Hints over Annotations**

Uses `inspect.signature()` to extract type hints rather than manual annotation parsing.

**Pros:**
- Handles various annotation styles
- Works with inherited annotations
- Standard library integration

**Cons:**
- Slightly slower than direct attribute access
- Requires Python 3.10+

### 2. **Frame Inspection**

Uses `inspect.currentframe()` to find the caller's namespace.

**Pros:**
- No need for explicit namespace argument
- Cleaner decorator API
- Works with metaclasses

**Cons:**
- May fail in some environments (PyPy, Jython)
- Slight performance overhead
- Harder to debug

### 3. **First Match Wins**

Returns the first matching overload rather than finding the "best" match.

**Pros:**
- Faster (no scoring logic)
- Predictable (order matters)
- Simple to understand

**Cons:**
- Users must order overloads carefully
- No automatic specificity ranking

### 4. **Descriptor Protocol for Methods**

Uses Python's descriptor protocol rather than wrapper functions.

**Pros:**
- Works with all Python method types
- Compatible with metaclasses
- No wrapper overhead

**Cons:**
- More complex implementation
- Subtle interactions with `@classmethod`, `@staticmethod`

## Future Improvements

- [ ] Thread-safe caching with locks
- [ ] Generic type support (`List[int]`, etc.)
- [ ] Better error messages with suggestions
- [ ] Performance profiling tools
- [ ] Type checking with mypy plugin
- [ ] Support for `*args` and `**kwargs`
- [ ] Pattern matching style overloads

## Summary

PyOverload provides a clean, Pythonic way to define function overloading using:

1. **Simple decorator syntax** for ease of use
2. **Type-based dispatch** for automatic resolution
3. **Caching** for performance
4. **Metaclass support** for class methods
5. **Descriptor protocol** for method binding

The architecture balances simplicity, performance, and compatibility with Python's design principles.
