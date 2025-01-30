import os
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging
from sphinx import addnodes  
from .fortran_parser import parse_fortran_file

logger = logging.getLogger(__name__)

class AutoFortranDirective(Directive):
    """
    A Sphinx directive to automatically document Fortran APIs with docstrings,
    subroutines, functions, and types styled similarly to Python.
    """
    has_content = True
    required_arguments = 1  # The path to the Fortran file
    
    def run(self):
        env = self.state.document.settings.env
        docmarker = env.app.config.fspx_docstring_character 
        file_path = self.arguments[0]
        
        if not os.path.isabs(file_path):
            file_path = os.path.join(env.srcdir, file_path)

        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist")
            return []
        
        fortran_data = parse_fortran_file(file_path, docmarker)
        
        section_node = nodes.section(ids=['fortran-api'])

        # Document modules
        if fortran_data['modules']:
            for mod in fortran_data['modules']:
                section_node += self.create_signature("module", mod['name'], mod['doc'])

        # Document submodules
        if fortran_data['submodules']:
            for submod in fortran_data['submodules']:
                section_node += self.create_signature("submodule", 
                    submod['name'],
                    submod['doc'],
                    parent=submod['parent']
                )

        # Document derived types
        if fortran_data['types']:
            for derived_type in fortran_data['types']:
                section_node += self.create_signature("type", 
                    derived_type['name'], 
                    derived_type['doc'], 
                    members=derived_type['members'], 
                    procedures=derived_type['procedures']
                )

        # Document subroutines
        if fortran_data['subroutines']:
            for subroutine in fortran_data['subroutines']:
                section_node += self.create_signature("subroutine", 
                    subroutine['name'], 
                    subroutine['doc'], 
                    subroutine['args'],
                    attributes=subroutine['attributes']
                )

        # Document functions
        if fortran_data['functions']:
            for func in fortran_data['functions']:
                section_node += self.create_signature("function", 
                    func['name'], 
                    func['doc'], 
                    func['args'], 
                    func['result'],
                    attributes=func['attributes']
                )

        return [section_node]

    def create_signature(self, element_type, name, 
                         docstring=None, 
                         args=None, 
                         result=None, 
                         members=None, 
                         procedures=None, 
                         attributes=None,
                         parent=None
                         ):
        """
        Create a styled signature for subroutines, functions, and types.
        For functions, the result variable is displayed outside the parentheses.
        """
        # Create the description node using Sphinx-specific addnodes
        desc = addnodes.desc()

        # Signature (header)
        sig = addnodes.desc_signature('', '')
        # Include attributes (e.g., "pure", "elemental") before the element type
        attr_text = f"{attributes} " if attributes else ""
        parent_text = f"({parent}) " if parent else "" # parent module for submodules
        sig += addnodes.desc_name(text=f"{attr_text}{element_type} {parent_text}{name}")

        # Handle arguments within parentheses
        if args:
            params = addnodes.desc_parameterlist()
            # Add only arguments with the attribute intent(in, out or inout).
            for arg_name, arg_info in args.items():
                if "intent" in arg_info["attributes"]:
                    param = addnodes.desc_parameter(text=f"{arg_name}")
                    params += param
            sig += params
        
        # Add result such as function_signature(args)->result
        if result:
            res = addnodes.desc_returns(text=f"{result:s}")
            sig += res

        desc += sig

        # Content (body)
        if docstring or args or result or members or procedures:
            content = addnodes.desc_content()

            # Add the docstring as the body content if present
            if docstring:
                for line in docstring.split("\n"):
                    content += nodes.paragraph(text=line)

            # Add argument descriptions and attributes
            if args:
                arg_list = nodes.definition_list()
                for arg_name, arg_info in args.items():
                    # Add only arguments with the attirbute intent (in, out, inout) or if it is the result.
                    if ("intent" in arg_info["attributes"]) or (arg_name == result):
                        term = nodes.term(text=f"{arg_name}: {arg_info['attributes']}")
                        definition = nodes.definition()
                        definition += nodes.paragraph(text=arg_info['description'])
                        item = nodes.definition_list_item('', term, definition)
                        arg_list += item
                content += arg_list

            # Add derived type members
            if members:
                member_list = nodes.definition_list()
                for member in members:
                    term = nodes.term(text=f"{member['name']}: {member['attributes']}")
                    definition = nodes.definition()
                    item = nodes.definition_list_item('', term, definition)
                    member_list += item
                content += member_list

            # Add type-bound procedures
            if procedures:
                procedure_list = nodes.bullet_list()
                for procedure in procedures:
                    procedure_item = nodes.list_item()
                    procedure_item += nodes.strong(text=f"{procedure['name']}")
                    procedure_list += procedure_item
                content += procedure_list

            content += nodes.math(text='') # adding this empty node seems to force sphinx to try and processes math expressions ...
            desc += content

        return desc
