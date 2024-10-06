# **WIP** THIS PROJECT IS A WORK IN PROGRESS.
Contributions are very much welcome!!

# FSPX: Fortran SPhinX

`fspx` is a Sphinx extension that provides automatic documentation for Modern Fortran code, including docstrings and procedure argument descriptions.

## Features

- Parses Fortran modules, subroutines, functions, and types.
- Supports docstrings using Fortran comments (`!>`).
- Automatically generates documentation with Sphinx.

## Installation

You can install the package using `pip`:

```bash
pip install fspx
```

If you want to install in developer mode for contributing, from the root folder:
```bash
pip install -e .
```

## Usage
To use the extension, add it to your Sphinx configuration (`conf.py`):
```python
extensions = [
    'fspx'
]
```

You can then use the `autofortran` directive as follows:

in your `.rst` files:
```rst
.. autofortran:: path/to/your/fortran/file.f90
```

in your `.md` files:
```
    ```{eval-rst}  
    .. autofortran:: path/to/your/fortran/file.f90
    ```
```
