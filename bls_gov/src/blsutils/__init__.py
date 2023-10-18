"""
The `__all__` attribute in a Python module serves as a way to specify which symbols (functions, classes, variables,
etc.) should be considered part of the module's public API. When you import a module using the `from module import *`
syntax or when using wildcard imports, the symbols listed in the `__all__` attribute are the ones that will be imported
into the importing module's namespace.

In your example, the `__all__` attribute is used to explicitly specify which names from the module should be considered
part of the module's public interface. This is a good practice for several reasons:

1. **Clarity:** It makes it clear which symbols are intended to be used by external code that imports the module. This
helps other developers understand which functions and classes are part of the module's API.

2. **Control:** It provides control over what is exposed to the outside world. You can limit the interface to just the
most important or commonly used symbols, even if the module contains many other internal functions and variables.

3. **Avoiding Name Clashes:** It helps prevent name clashes in the importing module. Without an `__all__` attribute, if
a module defines a lot of names, a wildcard import (`from module import *`) can overwrite or hide existing names in the
importing module, which can lead to unexpected behavior or bugs.

In your specific code, `__all__` lists the symbols that should be considered part of the public API for the module. When
someone imports this module using wildcard imports (`from module import *`), only the names listed in `__all__` will be
imported into their namespace, providing a clear and controlled interface to the module's functionality.
"""

from .bls import plot_bls_series_id
__all__ = [
    plot_bls_series_id
]
