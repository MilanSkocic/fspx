from .autofortran_directive import AutoFortranDirective

from .domains.fortran import FortranDomain

def setup(app):
    """
    Sphinx extension entry point for fspx.

    Registers the AutoFortranDirective for automatically documenting Fortran code.
    """
    app.add_directive("autofortran", AutoFortranDirective)
    app.add_config_value("fspx_docstring_character", "", "")

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
