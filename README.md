# General Purpose c programming language binding for Python

C programming language binding for python. This project intends to provide a general purpose binding to dynamically compiled library written in c programming language. The host library does not require any modification and can be incooperated into a python project easily. The binding requires path to the library (.so file in linux and .dll in windows) and path to the header file to get the names of the function and their arguments types and return types. This binding used pycparser to parse c header file and ctypes for datatype conversions.

Note: This project is still in development phase and many things are not yet implemented. There are some known bugs also, which need to be fixed. Therefore using this in production is not recommended.

## Example:

C library:
```c
// mylib.c

#include <math.h>

typedef struct RECT
{
    int x;
    int y;
} RECT;

int get_area(RECT a)
{
    return a.x * a.y;
}

int get_perimeter(RECT a)
{
    return 2 * (a.x + a.y);
}

double pi(int n)
{
    long int i;
    double sum = 0.0, term, pi;

    /* Applying Leibniz Formula */
    for(i = 0; i < n; i++)
    {
        term = pow(-1, i) / (2*i+1);
        sum += term;
    }
    pi = 4 * sum;

    return pi;
}
```
```c
// mylib.h

typedef struct RECT
{
    int x;
    int y;
} RECT;

int get_area(RECT a);
int get_perimeter(RECT a);
double pi(int n);
```
Compile above to shared library.

The library can be used in python as follows:
```python
from pyC import CLoad

mylib = CLoad("./mylib.so", "./mylib.c")

rect = mylib.RECT(12, 24)
area = mylib.get_area(rect)
perimeter = mylib.get_perimeter(rect)

print(f"RECT  x: {rect.x} y: {rect.y}")
print(f"rect area = {area}")
print(f"rect perimeter = {perimeter}")

pi = mylib.pi(500_000)

print(f"pi: {pi}")
```

## Stuff to implemented
- [ ] array support
- [ ] Function pointer support
- [ ] enum support
- [ ] union support

## Contribution
All contributions are welcomed. You can fork the project and create new PR, if you want to contribute. If the PR is related to a bud, creating a issue before creating the PR is recommended.
