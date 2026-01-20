# MethodOverload - Function and Method Overloading for Python

A powerful Python library that brings **function and method overloading** to Python, allowing you to define multiple implementations of the same function with different type signatures. Overloading is resolved at runtime based on the types of arguments passed.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-methodoverload-informational)](https://pypi.org/project/methodoverload/)

## Why MethodOverload?

Python doesn't natively support function overloading like Java or C++. If you define two functions with the same name, the second one overwrites the first. MethodOverload solves this problem elegantly:

```python
# Without MethodOverload - This doesn't work!
def add(a: int, b: int):
    return a + b

def add(a: str, b: str):  # Overwrites the previous function!
    return f"{a} {b}"

# With MethodOverload - This works perfectly!
from methodoverload import overload

@overload
def add(a: int, b: int):
    return a + b

@overload
def add(a: str, b: str):
    return f"{a} {b}"

print(add(1, 2))        # Output: 3
print(add("Hello", "World"))  # Output: Hello World
```

## Features

✨ **Simple & Intuitive** - Just use the `@overload` decorator  
✨ **Type-Safe** - Automatically matches the correct implementation based on type hints  
✨ **Instance Methods** - Full support for instance methods with metaclass integration  
✨ **Class Methods** - Works seamlessly with `@classmethod`  
✨ **Static Methods** - Compatible with `@staticmethod`  
✨ **Caching** - Fast resolution with built-in caching mechanism  
✨ **Clear Error Messages** - Helpful error messages when no matching overload is found  

## Installation

Install from PyPI:

```bash
pip install methodoverload
```

Or from source:

```bash
git clone https://github.com/mohdcodes/pyoverload.git
cd methodoverload
pip install -e .
```

## Quick Start

### 1. Basic Function Overloading

```python
from methodoverload import overload

@overload
def process(data: int):
    return data * 2

@overload
def process(data: str):
    return data.upper()

@overload
def process(data: list):
    return len(data)

print(process(5))              # Output: 10
print(process("hello"))        # Output: HELLO
print(process([1, 2, 3]))      # Output: 3
```

### 2. Instance Methods with Metaclass

```python
from methodoverload import overload, OverloadMeta

class Calculator(metaclass=OverloadMeta):
    @overload
    def compute(self, a: int, b: int):
        return a + b
    
    @overload
    def compute(self, a: str, b: str):
        return f"{a}{b}"
    
    @overload
    def compute(self, a: list, b: list):
        return a + b

calc = Calculator()
print(calc.compute(1, 2))           # Output: 3
print(calc.compute("Hello", "World"))  # Output: HelloWorld
print(calc.compute([1, 2], [3, 4]))    # Output: [1, 2, 3, 4]
```

### 3. Class Methods

```python
from methodoverload import overload, OverloadMeta

class Greeter(metaclass=OverloadMeta):
    @overload
    @classmethod
    def greet(cls, name: str):
        return f"Hello {name}"
    
    @overload
    @classmethod
    def greet(cls, count: int):
        return f"Greeting #{count}"

print(Greeter.greet("Alice"))  # Output: Hello Alice
print(Greeter.greet(42))       # Output: Greeting #42
```

### 4. Static Methods

```python
from methodoverload import overload, OverloadMeta

class Math(metaclass=OverloadMeta):
    @overload
    @staticmethod
    def multiply(a: int, b: int):
        return a * b
    
    @overload
    @staticmethod
    def multiply(a: float, b: float):
        return round(a * b, 2)

print(Math.multiply(3, 4))      # Output: 12
print(Math.multiply(3.5, 2.5))  # Output: 8.75
```

## How It Works

MethodOverload uses **type hints** to determine which implementation to call:

1. **Registration** - Each `@overload` decorated function is registered with its type signature
2. **Resolution** - When called, MethodOverload examines the argument types
3. **Matching** - Finds the implementation whose type signature matches the arguments
4. **Execution** - Calls the matching implementation
5. **Caching** - Results are cached for performance

### Type Matching Rules

- Arguments are matched against type hints using `isinstance()`
- The first matching overload is called
- If no overload matches, `NoMatchingOverloadError` is raised

```python
from methodoverload import overload

@overload
def process(data: str):
    return f"String: {data}"

@overload
def process(data: int):
    return f"Integer: {data}"

# This works!
process("hello")  # Output: String: hello
process(42)       # Output: Integer: 42

# This raises NoMatchingOverloadError
process(3.14)     # No matching overload for float!
```

## Advanced Usage

### Multiple Type Parameters

```python
from methodoverload import overload

@overload
def convert(value: int, to_type: str):
    return str(value)

@overload
def convert(value: str, to_type: int):
    return int(value)

@overload
def convert(value: list, to_type: tuple):
    return tuple(value)

print(convert(42, "str"))      # Output: "42"
print(convert("100", "int"))   # Output: 100
print(convert([1, 2, 3], tuple))  # Output: (1, 2, 3)
```

### Combining with Other Decorators

```python
from methodoverload import overload

@overload
def cached_process(data: int):
    print("Processing integer...")
    return data ** 2

@overload
def cached_process(data: str):
    print("Processing string...")
    return data.upper()

# Each call with the same type is cached for performance
print(cached_process(5))     # Processing integer...
print(cached_process(5))     # (cached - no print)
```

## Error Handling

When no matching overload is found, you get a helpful error message:

```python
from methodoverload import overload, NoMatchingOverloadError

@overload
def add(a: int, b: int):
    return a + b

try:
    add("1", "2")  # No string overload defined
except NoMatchingOverloadError as e:
    print(e)
    # Output: No matching overload found for 'add' with args=('1', '2'), kwargs={}
```




## Examples

See the `examples/` directory for more detailed examples:

- **basic.py** - Free function overloading
- **classmethod.py** - Class method overloading
- **staticmethod.py** - Static method overloading
- **types.py** - Complex type examples

Run an example:

```bash
python -m examples.basic
```

## Architecture

### Core Components

1. **OverloadedFunction** - Container for multiple implementations with dispatch logic
2. **@overload Decorator** - Registers function implementations
3. **OverloadMeta Metaclass** - Merges overloads in class definitions
4. **OverloadCache** - Caches resolved overloads for performance

### Design Principles

- **Framework-agnostic** - No dependencies, works with any Python code
- **Type-driven** - Uses type hints for dispatch
- **Descriptor protocol** - Integrates seamlessly with Python's method binding
- **Efficient** - Built-in caching for repeated calls

## Limitations & Best Practices

### Current Limitations

- Overloads are resolved at runtime (not compile-time)
- Only supports positional and keyword arguments
- Type matching uses `isinstance()` (no generic types like `List[int]`)

### Best Practices

✓ Always use type hints for all parameters  
✓ Keep implementations focused and simple  
✓ Use descriptive function names  
✓ Test all overload combinations  
✓ Document which types are supported  

```python
# Good
@overload
def process(data: str) -> str:
    """Process string data and return uppercase."""
    return data.upper()

# Avoid - Missing type hints
@overload
def process(data):
    return data.upper()
```


## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Mohd Arbaaz Siddiqui** - Original author
- See [Contributors](https://github.com/mohdcodes/pyoverload/graphs/contributors) for the full list

## Support

- 📖 [Documentation](https://github.com/mohdcodes/pyoverload)
- 🐛 [Report Issues](https://github.com/mohdcodes/pyoverload)
- 💬 [Discussions](https://github.com/mohdcodes/pyoverload)

## Changelog

### Version 0.1.0 (Current)
- Initial release
- Free function overloading
- Instance method overloading with OverloadMeta
- Class method and static method support
- Built-in caching for performance
- Type hint-based dispatch
- Comprehensive error messages

## Citation

If you use MethodOverload in your research or project, please cite:

```bibtex
@software{methodoverload2024,
  title={MethodOverload: Function and Method Overloading for Python},
  author={Siddiqui, Mohd Arbaaz},
  year={2024},
  url={https://github.com/mohdcodes/pyoverload}
}
```

---

**Made with ❤️ by MOHD ARBAAZ SIDDIQUI**


