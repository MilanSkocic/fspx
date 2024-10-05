import os
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util import logging
from .fortran_parser import parse_fortran_file

logger = logging.getLogger(__name__)

class AutoFortranDirective(Directive):
    """
    A Sphinx directive to automatically document Fortran APIs with docstrings.
    """
    has_content = True
    required_arguments = 1  # The path to the Fortran file
    
    def run(self):
        env = self.state.document.settings.env
        file_path = self.arguments[0]
        
        if not os.path.isabs(file_path):
            file_path = os.path.join(env.srcdir, file_path)

        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} does not exist")
            return []
        
        fortran_data = parse_fortran_file(file_path)
        
        section_node = nodes.section(ids=['fortran-api'])
        section_node += nodes.title(text="Fortran API Documentation")

        # Document modules
        if fortran_data['modules']:
            section_node += nodes.subtitle(text="Modules")
            for mod in fortran_data['modules']:
                paragraph = nodes.paragraph()
                paragraph += nodes.strong(text=f"Module: {mod['name']}")
                if mod['doc']:
                    paragraph += nodes.paragraph(text=mod['doc'])
                section_node += paragraph
        
        # Document subroutines
        if fortran_data['subroutines']:
            section_node += nodes.subtitle(text="Subroutines")
            for subroutine in fortran_data['subroutines']:
                paragraph = nodes.paragraph()
                paragraph += nodes.strong(text=f"Subroutine: {subroutine['name']}")
                if subroutine['doc']:
                    paragraph += nodes.paragraph(text=subroutine['doc'])
                
                # Display arguments and their docstrings
                if subroutine['args']:
                    arg_list = nodes.bullet_list()
                    for arg_name, arg_doc in subroutine['args'].items():
                        item = nodes.list_item()
                        item += nodes.strong(text=arg_name)
                        if arg_doc:
                            item += nodes.paragraph(text=arg_doc)
                        else:
                            item += nodes.paragraph(text="No description provided.")
                        arg_list += item
                    paragraph += arg_list

                section_node += paragraph
        
        # Document functions
        if fortran_data['functions']:
            section_node += nodes.subtitle(text="Functions")
            for func in fortran_data['functions']:
                paragraph = nodes.paragraph()
                paragraph += nodes.strong(text=f"Function: {func['name']}")
                if func['doc']:
                    paragraph += nodes.paragraph(text=func['doc'])
                
                # Display arguments and their docstrings
                if func['args']:
                    arg_list = nodes.bullet_list()
                    for arg_name, arg_doc in func['args'].items():
                        item = nodes.list_item()
                        item += nodes.strong(text=arg_name)
                        if arg_doc:
                            item += nodes.paragraph(text=arg_doc)
                        else:
                            item += nodes.paragraph(text="No description provided.")
                        arg_list += item
                    paragraph += arg_list

                section_node += paragraph

        # Document derived types
        if fortran_data['types']:
            section_node += nodes.subtitle(text="Derived Types")
            for derived_type in fortran_data['types']:
                paragraph = nodes.paragraph()
                paragraph += nodes.strong(text=f"Type: {derived_type['name']}")
                if derived_type['doc']:
                    paragraph += nodes.paragraph(text=derived_type['doc'])
                section_node += paragraph

        return [section_node]
