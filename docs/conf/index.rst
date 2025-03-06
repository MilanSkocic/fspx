=====================
Sphinx `conf.py`
=====================

`fspx_docstring_character` defined in Sphinx configuration is a sequence of 4 characters
which corresponds to 4 types of markers defined in the backend i.e. Ford.

The 4 types of markers are defined below:

 * `docmarker` which used as a documentation marker for:
    * the documentation defined under the declarations of modules, functions, subroutines and types
    * the inline documentation e.g. the function arguments
 * `docmarker\_alt` which is used as an alternate marker for the documentation as it is the case for docmarker 
    except that the inline documentation is not accepted
 * `predocmark` which used as a documentation marker for:
    * the documentation defined under the declarations of modules, functions, subroutines, types, and variables
    * the inline documentation is not accepted
 * `predocmark\_alt` which used as an alternate documentation marker for:
    * the documentation defined under the declarations of modules, functions, subroutines, types, and variables as it is the case for predocmarker.
    * the inline documentation is not accepted

If provided in the `conf.py`, it needs to be a strict sequence of 4 characters. 
The default sequence defined is `!*>|`. 
The comment marker `!` in front of those markers is implicit even for source code written in F77. 
Actually, Ford converts everything to free form before parsing the code.
All the 4 markers must be unique otherwise Ford will complain and fail.


.. code-block:: python

    fspx_docstring_character = "!*>|" # default sequence
    fspx_docstring_character = ">*@#" # custom sequence