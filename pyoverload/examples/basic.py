# examples/basic.py
from methodoverload.decorators import overload

print("===== FREE FUNCTION OVERLOAD =====")

@overload
def add(a: int, b: int):
    print("→ int,int overload called")
    return a + b

@overload
def add(a: str, b: str):
    print("→ str,str overload called")
    return a + b

print(add(1, 2))       # Output: → int,int overload called\n3
print(add("x", "y"))   # Output: → str,str overload called\nxy
