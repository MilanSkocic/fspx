"""The Fortran Domain"""
from sphinx.domains import Domain
from ._object import FortranField

class FortranDomain(Domain):
    """The Fortran Domain"""

    name = "f"
    label = "Fortran"


    
