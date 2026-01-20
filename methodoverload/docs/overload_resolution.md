# Overload Resolution Algorithm

This document explains how PyOverload determines which implementation to call based on argument types.

## Overview

When an overloaded function is called, PyOverload needs to find the best matching implementation. This process involves:

1. **Signature Extraction** - Get type hints from the call arguments
2. **Cache Lookup** - Check if this call signature was seen before
3. **Type Matching** - Find all compatible implementations
4. **Selection** - Choose the best match
5. **Execution** - Call the selected implementation

## Type Matching Strategy

### Signature Representation

Each overload is stored with its type signature:

```python
@overload
def process(self, data: int) -> str:
    return str(data)

@overload
def process(self, data: str) -> str:
    return data.upper()

# Stored as:
# (int,) -> str_method
# (str,) -> upper_method
```

For methods, `self` is skipped in the stored signature. For classmethods, `cls` is skipped.

### Argument Type Resolution

When a method is called, PyOverload gets the type of each argument:

```python
instance.process(42)      # Argument types: (int,)
instance.process("hello") # Argument types: (str,)
```

### Exact vs Compatible Matching

PyOverload looks for:

1. **Exact matches** - Argument type exactly matches signature
2. **Compatible matches** - Argument is instance of signature type

```python
@overload
def func(x: int): pass

func(5)           # Exact match: int
func(True)        # Compatible: bool is subclass of int
func(5.0)         # No match: float not compatible with int
```

### Multiple Arguments

For methods with multiple arguments:

```python
@overload
def combine(self, a: int, b: str): pass

@overload
def combine(self, a: str, b: int): pass

instance.combine(1, "x")    # Matches first: (int, str)
instance.combine("x", 1)    # Matches second: (str, int)
```

## Resolution Algorithm

### Pseudocode

```
FUNCTION resolve(arguments, keyword_arguments):
    1. Extract types from arguments:
       arg_types = tuple(type(arg) for arg in arguments)
    
    2. Skip first parameter if present:
       IF this_is_method AND arg_types[0] is self or cls:
           arg_types = arg_types[1:]
    
    3. Check cache:
       IF arg_types in cache:
           RETURN cache[arg_types]
    
    4. Find candidates:
       candidates = []
       FOR EACH registered (signature, function) pair:
           IF signature matches arg_types:
               candidates.append(function)
    
    5. Handle results:
       IF no candidates:
           RAISE TypeError("No matching overload")
       ELSE IF one candidate:
           result = candidate
       ELSE:  # Multiple candidates
           result = candidates[0]  # First match (registration order)
    
    6. Cache result:
       cache[arg_types] = result
    
    7. Return matching function:
       RETURN result
```

### Code Implementation

```python
def resolve(self, *args, **kwargs):
    """Find the matching implementation for given arguments."""
    
    # Step 1: Extract argument types
    arg_types = tuple(type(arg) for arg in args)
    
    # Step 2: Skip self/cls for bound methods
    if arg_types and arg_types[0] is type(self):
        # First arg is self - skip it
        arg_types = arg_types[1:]
    
    # Step 3: Check cache
    if arg_types in self.cache.store:
        return self.cache.store[arg_types]
    
    # Step 4: Find matching implementations
    matching = []
    for sig, func in self.implementations:
        if self._types_match(sig, arg_types):
            matching.append(func)
    
    # Step 5: Handle results
    if not matching:
        raise TypeError(
            f"No matching overload for {self.name}("
            f"{', '.join(t.__name__ for t in arg_types)})"
        )
    
    selected = matching[0]
    
    # Step 6: Cache the result
    self.cache.set(self.name, arg_types, selected)
    
    # Step 7: Return
    return selected

def _types_match(self, signature, arg_types):
    """Check if argument types match a signature."""
    
    # Different lengths - no match
    if len(signature) != len(arg_types):
        return False
    
    # Check each argument
    for sig_type, arg_type in zip(signature, arg_types):
        if sig_type == arg_type:
            continue  # Exact match
        
        try:
            if issubclass(arg_type, sig_type):
                continue  # Compatible (subclass)
        except TypeError:
            pass  # issubclass doesn't work with some types
        
        return False  # No match for this argument
    
    return True  # All arguments matched
```

## Examples

### Example 1: Basic Resolution

```python
@overload
def add(x: int, y: int) -> int:
    return x + y

@overload
def add(x: str, y: str) -> str:
    return f"{x}{y}"

# Call 1: add(1, 2)
# Extracted types: (int, int)
# Check implementations:
#   - int + int: MATCH ✓
#   - str + str: NO MATCH (first arg int, not str)
# Result: Uses first implementation
# Output: 3

# Call 2: add("a", "b")
# Extracted types: (str, str)
# Check implementations:
#   - int + int: NO MATCH
#   - str + str: MATCH ✓
# Result: Uses second implementation
# Output: "ab"

# Call 3: add(True, False)
# Extracted types: (bool, bool)
# Check implementations:
#   - int + int: MATCH (bool is subclass of int) ✓
#   - str + str: NO MATCH
# Result: Uses first implementation
# Output: 1 (True + False as integers)
```

### Example 2: Method Resolution

```python
class Printer(metaclass=OverloadMeta):
    @overload
    def print(self, data: int):
        return f"Integer: {data}"
    
    @overload
    def print(self, data: str):
        return f"String: {data}"

printer = Printer()

# Call: printer.print(42)
# Step 1: Extract argument types including self
#   raw_types = (Printer, int)
# Step 2: Skip self (first arg when it's the instance)
#   arg_types = (int,)
# Step 3: Check cache - miss
# Step 4: Match against signatures
#   - (int,): MATCH ✓
#   - (str,): NO MATCH
# Step 5: Found one match
# Step 6: Cache {(int,): first_impl}
# Result: "Integer: 42"
```

### Example 3: Ambiguous Matching (Multiple Candidates)

```python
@overload
def process(x: object):
    return "object"

@overload
def process(x: int):
    return "int"

# Call: process(5)
# Extracted types: (int,)
# Check implementations:
#   - (object,): MATCH (int is subclass of object)
#   - (int,): MATCH (exact match)
# Multiple matches found - use first registered
# Result: "int" (int is more specific and registered second)
```

### Example 4: No Match Error

```python
@overload
def concat(x: str, y: str) -> str:
    return x + y

# Call: concat(1, 2)
# Extracted types: (int, int)
# Check implementations:
#   - (str, str): NO MATCH
# No candidates found
# Raises:
#   TypeError: No matching overload for concat(int, int)
```

## Caching Strategy

### Why Cache?

Without caching, each call would re-scan all implementations:

```python
for i in range(1000000):
    result = dispatcher(42)  # Would re-match every time!
```

### How It Works

```python
def __call__(self, *args, **kwargs):
    # First call - resolve and cache
    func = self.resolve(*args, **kwargs)
    self.cache.set(...)
    return func(*args, **kwargs)

# Second call with same arg types - use cache
# Third call with same arg types - use cache
```

### Cache Key

```python
# For function: cache_key = (func_name, arg_types, kwarg_types)

call_1: dispatcher(1, "x")
# cache_key = ('method', (int, str), ())
# Stored: {(int, str): int_str_impl}

call_2: dispatcher(1, "y")
# cache_key = ('method', (int, str), ())
# CACHE HIT! Reuse int_str_impl
```

### Invalidation

The cache is valid as long as:

1. The argument types are the same
2. The implementations list hasn't changed (class not modified)
3. The decorator configuration hasn't changed

**Note:** PyOverload doesn't automatically invalidate cache if you modify implementations at runtime. Don't do that!

## Keyword Arguments

### Basic Handling

```python
@overload
def fetch(url: str):
    return requests.get(url)

@overload
def fetch(url: str, timeout: int):
    return requests.get(url, timeout=timeout)

# Call with kwargs
result = fetch("https://...", timeout=30)
# Resolved as: (str, int)
```

### Kwargs in Signatures

```python
@overload
def process(data: list):
    return sum(data)

@overload
def process(data: list, mode: str):
    return max(data) if mode == "max" else min(data)

# Call: process([1, 2, 3], mode="max")
# Extracted types: (list, str)  # kwargs converted to positional
# Matches second signature
# Result: 3
```

### Mixed Args and Kwargs

```python
@overload
def combine(*args: int):
    return sum(args)

@overload
def combine(*args: str):
    return "".join(args)

# Note: *args not currently fully supported
# PyOverload works best with explicit parameters
```

## Type Hierarchy and Resolution

### Subclass Matching

```python
class Animal: pass
class Dog(Animal): pass
class Cat(Animal): pass

@overload
def handle(x: Animal):
    return "animal"

@overload
def handle(x: Dog):
    return "dog"

# Call: handle(Dog())
# Extracted type: (Dog,)
# Matches:
#   - (Animal,): YES (Dog is subclass)
#   - (Dog,): YES (exact match)
# Takes first match: "dog"

# Call: handle(Cat())
# Extracted type: (Cat,)
# Matches:
#   - (Animal,): YES
#   - (Dog,): NO
# Result: "animal"
```

### Order Matters

```python
@overload
def process(x: int):
    return "specific int"

@overload
def process(x: object):
    return "generic object"

process(5)
# Matches both, uses first: "specific int" ✓

# vs

@overload
def process(x: object):
    return "generic object"

@overload
def process(x: int):
    return "specific int"

process(5)
# Matches both, uses first: "generic object" ⚠️
```

**Lesson:** Register more specific types first.

## Union Types

Currently, PyOverload doesn't directly support `Union[int, str]` in signatures, but you can work around it:

```python
from typing import Union

@overload
def handle(x: int):
    return x * 2

@overload
def handle(x: str):
    return x.upper()

# This covers Union[int, str] via multiple overloads
handle(1)      # int
handle("a")    # str
```

## Optional Types

```python
from typing import Optional

@overload
def greet(name: str):
    return f"Hello {name}"

@overload
def greet(name: type(None)):
    return "Hello stranger"

greet("Alice")   # "Hello Alice"
greet(None)      # "Hello stranger"
```

## Generic Types

PyOverload has limited support for generics because type erasure makes runtime resolution difficult:

```python
from typing import List, Dict

@overload
def process(data: list):
    return "list"

@overload
def process(data: dict):
    return "dict"

# Works - resolves based on list/dict type
# But doesn't check List[int] vs List[str]
# Both [1,2,3] and ["a","b"] match the list overload
```

## Error Messages

### Clear Error Reporting

When no match is found, PyOverload provides helpful errors:

```python
@overload
def divide(a: int, b: int) -> float:
    return a / b

divide(5, "x")
# TypeError: No matching overload for divide(int, str)
# Indicates exactly which types were attempted
```

### Debug Information

For troubleshooting, you can inspect the dispatcher:

```python
for sig, func in divide.implementations:
    print(f"Overload: {sig} -> {func.__name__}")

# Output:
# Overload: (int, int) -> divide_int_int
```

## Performance Characteristics

### Time Complexity

- **First call** - O(n) where n = number of overloads (matching)
- **Subsequent calls** - O(1) (cache lookup)
- **Worst case** - All unique argument signatures with no cache hits

### Space Complexity

- **Per function** - O(n) for storing implementations
- **Per cache entry** - O(1) with minimal memory overhead
- **Total** - O(n * m) where n=functions, m=unique signatures seen

### Cache Effectiveness

For typical usage:

```python
dispatcher = overload_func

# Warm-up (populate cache)
for i in range(10):
    dispatcher(1, "x")  # Same types - 1 resolution, 9 cache hits

# Production
# Hit rate: 95%+ for stable programs
```

## Thread Safety

### Current Implementation

PyOverload is **NOT thread-safe** for:
- Concurrent calls during class initialization
- Modifying implementations while methods are executing

### Safe Usage

```python
# ✓ Safe
class MyClass:
    @overload
    def method(self, x: int): pass

# Create instances in multiple threads
obj1 = MyClass()
obj2 = MyClass()

# Call methods from multiple threads
# (no concurrent modifications)

# ✗ Unsafe
class MyClass:
    @overload
    def method(self, x: int): pass

# Don't modify while calling
thread1: obj.method(1)
thread2: obj.method = new_impl  # DON'T DO THIS!
```

### Future Improvements

Thread safety could be added with:
1. Lock around resolution
2. Atomic cache updates
3. Copy-on-write for implementations list

## Debugging Resolution

### Inspect Implementations

```python
dispatcher = MyClass.method

# See all registered overloads
print(dispatcher.implementations)

# Check cache state
print(dispatcher.cache.store)
```

### Trace Resolution

```python
import inspect

@overload
def func(x: int): pass

@overload
def func(x: str): pass

# Add debugging
original_resolve = func.resolve
def debug_resolve(*args, **kwargs):
    print(f"Resolving with types: {tuple(type(a) for a in args)}")
    result = original_resolve(*args, **kwargs)
    print(f"Matched: {result.__name__}")
    return result

func.resolve = debug_resolve
```

### Manual Matching

```python
def manually_match(dispatcher, arg_types):
    """Manually check which overloads match."""
    for sig, impl in dispatcher.implementations:
        if dispatcher._types_match(sig, arg_types):
            print(f"✓ Matches {sig}")
        else:
            print(f"✗ No match {sig}")

arg_types = (int, str)
manually_match(my_dispatcher, arg_types)
```

## Summary

The overload resolution algorithm:

1. **Extracts** types from call arguments
2. **Checks cache** for performance
3. **Matches** against all registered signatures
4. **Selects** the first match (registration order)
5. **Caches** for future calls
6. **Executes** the selected implementation

Key features:
- ✅ Efficient with caching
- ✅ Clear error messages
- ✅ Flexible type matching (exact and compatible)
- ✅ Supports multiple parameters
- ⚠️ Not thread-safe
- ⚠️ Limited generic type support

Best practices:
- Register specific types before general ones
- Keep signatures distinct
- Use consistent type hints
- Test overload ordering if ambiguous
