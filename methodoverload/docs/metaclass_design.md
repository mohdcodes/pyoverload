# Metaclass Design for methodoverload

This document explains the design and implementation of the `OverloadMeta` metaclass and why it's necessary for class method overloading.

## Problem: Method Overloading in Classes

Without a metaclass, defining multiple overloads of the same method in a class causes the second definition to overwrite the first:

```python
class MyClass:
    @overload
    def method(self, x: int):
        return x * 2
    
    @overload  # This overwrites the previous method!
    def method(self, x: str):
        return x.upper()
```

The second `method` completely replaces the first, so we lose one implementation.

## Solution: OverloadMeta Metaclass

The `OverloadMeta` metaclass solves this by:

1. **Collecting** all overload definitions during class creation
2. **Merging** implementations from multiple definitions
3. **Replacing** each method with a single merged dispatcher

## How It Works

### Step 1: Class Body Execution

During class definition, Python executes the class body:

```python
class MyClass(metaclass=OverloadMeta):
    @overload
    def method(self, x: int):
        pass
    
    @overload
    def method(self, x: str):
        pass
```

Each `@overload` decorator creates an `OverloadedFunction` with one implementation. The second definition stores its dispatcher in the same name, potentially overwriting.

### Step 2: Metaclass Interception

When the class body finishes executing, Python calls:

```python
type.__new__(mcls, name, bases, namespace)
```

Our metaclass intercepts this to:
1. Inspect the `namespace` dict
2. Find all `OverloadedFunction` instances
3. Merge their implementations
4. Store the merged dispatcher back

```python
class OverloadMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        overloads = {}
        
        # Step 1: Collect overloaded definitions
        for attr_name, obj in namespace.items():
            dispatcher = None
            wrapper = None
            
            # Handle wrapped dispatchers (classmethod, staticmethod)
            if isinstance(obj, (classmethod, staticmethod)):
                wrapper = type(obj)
                if isinstance(obj.__func__, OverloadedFunction):
                    dispatcher = obj.__func__
            # Handle unwrapped dispatchers
            elif isinstance(obj, OverloadedFunction):
                dispatcher = obj
            
            if dispatcher is not None:
                overloads.setdefault(attr_name, []).append((dispatcher, wrapper))
        
        # Step 2: Merge overloads
        for method_name, dispatchers_info in overloads.items():
            merged = OverloadedFunction(name=method_name)
            wrapper = None
            
            for dispatcher, disp_wrapper in dispatchers_info:
                # Track wrapper type
                if disp_wrapper is not None:
                    wrapper = disp_wrapper
                
                # Merge implementations
                for sig, func in dispatcher.implementations:
                    merged.implementations.append((sig, func))
            
            # Step 3: Re-wrap if necessary
            if wrapper is not None:
                namespace[method_name] = wrapper(merged)
            else:
                namespace[method_name] = merged
        
        return super().__new__(mcls, name, bases, namespace)
```

### Step 3: Class Creation

The modified `namespace` is passed to the parent metaclass, creating a class with a single merged dispatcher for each method.

## Example: Step-by-Step Execution

```python
class Calculator(metaclass=OverloadMeta):
    @overload
    def add(self, x: int, y: int):
        return x + y
    
    @overload
    def add(self, x: str, y: str):
        return f"{x}{y}"
```

**Timeline:**

1. **Line 3** - `@overload` called for `int` version
   - Creates `OverloadedFunction` with one implementation
   - Stores in `namespace['add']`

2. **Line 7** - `@overload` called for `str` version
   - Finds existing `OverloadedFunction` in namespace
   - Registers new implementation
   - Stores back in `namespace['add']`

3. **After class body** - `OverloadMeta.__new__` called
   - Finds `namespace['add']` is an `OverloadedFunction`
   - Merges (in this case, already merged by decorator)
   - Creates class with merged dispatcher

4. **Usage**
   ```python
   calc = Calculator()
   calc.add(1, 2)        # Dispatches to int version
   calc.add("a", "b")    # Dispatches to str version
   ```

## Handling Wrapped Methods

The metaclass also handles `@classmethod` and `@staticmethod`:

```python
class MyClass(metaclass=OverloadMeta):
    @overload
    @classmethod
    def greet(cls, name: str):
        return f"Hello {name}"
    
    @overload
    @classmethod
    def greet(cls, count: int):
        return f"Greeting #{count}"
```

**Key handling:**

```python
# Detect wrapper
if isinstance(obj, classmethod):
    wrapper = classmethod
    dispatcher = obj.__func__  # Get wrapped OverloadedFunction
else:
    wrapper = None
    dispatcher = obj

# ... merge implementations ...

# Re-wrap at the end
if wrapper:
    namespace[method_name] = wrapper(merged)
```

This ensures:
- The original wrapper type is preserved
- The dispatcher is properly wrapped
- `@classmethod` and `@staticmethod` still work correctly

## Comparison: With and Without Metaclass

### Without Metaclass

```python
class MyClass:
    @overload
    def method(self, x: int):
        return x * 2
    
    @overload  # ERROR: Second definition overwrites first!
    def method(self, x: str):
        return x.upper()

# Only str version works!
MyClass().method(5)      # TypeError
MyClass().method("hi")   # "HI"
```

### With Metaclass

```python
class MyClass(metaclass=OverloadMeta):
    @overload
    def method(self, x: int):
        return x * 2
    
    @overload  # Works! Both versions available
    def method(self, x: str):
        return x.upper()

# Both work!
MyClass().method(5)      # 10
MyClass().method("hi")   # "HI"
```

## Why Not Use a Decorator Instead?

Could we use a class decorator instead of a metaclass?

```python
@merge_overloads
class MyClass:
    @overload
    def method(self, x: int): ...
    
    @overload
    def method(self, x: str): ...
```

**Issues with decorator approach:**
1. **Timing** - Decorator runs AFTER class creation, too late to fix overwriting
2. **Namespace** - Class decorator can't access original namespace dict
3. **Inheritance** - Metaclass properly handles inherited methods

**Metaclass advantages:**
1. **Timing** - Runs DURING class creation before methods are finalized
2. **Access** - Direct access to namespace dict
3. **Integration** - Naturally integrates with Python's class creation protocol
4. **Inheritance** - Properly inherits metaclass behavior in subclasses

## Edge Cases and Gotchas

### 1. Mixing Overloads Across Multiple Passes

```python
class MyClass(metaclass=OverloadMeta):
    @overload
    def method(self, x: int): pass
    
    @overload
    def method(self, x: str): pass
```

Both are found and merged in the same metaclass `__new__` call. ✅ Works correctly.

### 2. Inheritance with Metaclass

```python
class Base(metaclass=OverloadMeta):
    @overload
    def method(self, x: int): pass

class Derived(Base):
    @overload
    def method(self, x: str): pass
```

**Note:** `Derived` doesn't automatically inherit Base's overloads. Each class has its own set. To combine, you'd need to explicitly re-define or use a different pattern.

### 3. Multiple Inheritance

```python
class A(metaclass=OverloadMeta):
    pass

class B(metaclass=OverloadMeta):
    pass

class C(A, B):  # ✅ Works - metaclass is inherited
    pass
```

Python uses the most derived metaclass (rightmost in MRO).

### 4. Overloads Added After Class Definition

```python
class MyClass(metaclass=OverloadMeta):
    @overload
    def method(self, x: int): pass

# Trying to add overload after class definition
# This WON'T be merged!
MyClass.method = overload(lambda self, x: str: ...)
```

Overloads must be defined inside the class body. Adding them later requires manual dispatcher creation.

## Performance Implications

### Metaclass Overhead

- **Class creation** - Minimal, O(n) where n = number of methods
- **Method calls** - No overhead, dispatcher is set up at class creation
- **Runtime** - Zero metaclass involvement (works through descriptor protocol)

### Memory

- One `OverloadedFunction` per method instead of multiple function objects
- Slightly more memory for signature storage

## Metaclass Best Practices

### Do's ✅

1. **Define all overloads in class body**
   ```python
   class MyClass(metaclass=OverloadMeta):
       @overload
       def method(self, x: int): pass
       
       @overload
       def method(self, x: str): pass
   ```

2. **Mix with other decorators on individual methods**
   ```python
   @overload
   @property
   def prop(self) -> int: pass
   ```

3. **Use with class/static methods**
   ```python
   @overload
   @classmethod
   def method(cls, x: int): pass
   ```

### Don'ts ❌

1. **Don't mix metaclasses without proper inheritance**
   ```python
   class MyMeta(OverloadMeta):
       pass
   
   class MyClass(metaclass=MyMeta):  # ✅ OK
       pass
   ```

2. **Don't expect late binding of overloads**
   ```python
   class MyClass(metaclass=OverloadMeta):
       @overload
       def method(self, x: int): pass
   
   # This won't be automatically merged
   def str_method(self, x: str): pass
   MyClass.method = overload(str_method)
   ```

3. **Don't forget metaclass when subclassing**
   ```python
   # Child class automatically gets the metaclass
   class Child(Parent):  # ✅ Works
       @overload
       def method(self, x: float): pass
   ```

## Alternative Approaches

### Without Metaclass: Manual Registration

```python
class MyClass:
    def __init__(self):
        self._dispatcher = OverloadedFunction('method')
        self._dispatcher.register(self._method_int)
        self._dispatcher.register(self._method_str)
    
    def method(self, x):
        return self._dispatcher(x)
    
    def _method_int(self, x: int):
        return x * 2
    
    def _method_str(self, x: str):
        return x.upper()
```

**Disadvantages:**
- Verbose and error-prone
- Requires manual dispatcher management
- Less Pythonic

### Using `__init_subclass__`

```python
class OverloadBase:
    def __init_subclass__(cls):
        # Similar to metaclass, but runs on subclass creation
        # Merges overloads here
        pass
```

**Works but:**
- Runs per subclass, not per class
- More complex to implement correctly

## Summary

The `OverloadMeta` metaclass provides:

1. **Clean syntax** - Natural overload definition
2. **Automatic merging** - Handles multiple overload definitions
3. **Proper integration** - Works with classmethods and staticmethods
4. **Python standard** - Uses metaclass protocol as intended
5. **Zero runtime cost** - Overhead only at class creation time

It's the right tool for this job because it operates at the correct point in Python's class creation lifecycle.
