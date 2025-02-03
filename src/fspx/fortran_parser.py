import re
from fparser.common.readfortran import FortranFileReader
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk, get_child
import fparser.two.Fortran2003 as fp2003
import fparser.two.Fortran2008 as fp2008
from fparser.two.Fortran2003 import Module, Derived_Type_Def, Subroutine_Subprogram, Function_Subprogram, Specification_Part, Implicit_Part, Comment
from fparser.two.Fortran2003 import Module_Stmt, Subroutine_Stmt, Function_Stmt, Derived_Type_Stmt
from fparser.two.Fortran2008 import Submodule, Submodule_Stmt

# Initialize Fortran 2008 parser
parser = ParserFactory().create(std="f2008")

def parse_fortran_file(file_path, docmarker:str="!>"):
    """
    Parse a Fortran file and extract the code structure (modules, subroutines, functions, types),
    including docstrings and argument descriptions from inline comments.
    """
    docstring = None
    fortran_data = {
        'modules': [],
        'submodules': [],
        'subroutines': [],
        'functions': [],
        'types': []
    }
    
    with open(file_path, 'r') as f:
        reader = FortranFileReader(f.name, ignore_comments=False)
        parse_tree = parser(reader)

        # Read the file line-by-line for docstring extraction
        lines = f.readlines()

    for node in walk(parse_tree):
        # Collect modules
        default_scope = "public"
        if isinstance(node, Module):
            content = get_child( node , fp2003.Specification_Part ).content
            docstring = extract_comments( content[0].children , docmarker)
            default_scope = extract_module_scope(node)
            public = extract_module_scopes(node, "public")
            fortran_data['modules'].append({
                'name': node.children[0].children[1].string,
                'doc': docstring,
                'public': public,
                'scope': scope,
            })

        # Collect submodules
        if isinstance(node, Submodule):
            content = get_child( node , fp2003.Specification_Part ).content
            docstring = extract_comments( content[0].children , docmarker)
            scope = extract_module_scope(node)
            fortran_data['submodules'].append({
                'name': node.children[0].children[1].string,
                'parent': node.children[0].children[0].children[0].string,
                'doc': docstring,
                'scope': scope,
            })
        
        # Collect subroutines
        if isinstance(node, Subroutine_Subprogram):
            name = get_child( get_child( node , fp2003.Subroutine_Stmt ), fp2003.Name ).string
            content = get_child( node , fp2003.Specification_Part ).content
            docstring = extract_comments( content[0].children , docmarker)
            args = extract_arguments( content[1:], docmarker )
            prefix = get_child( get_child( node , fp2003.Subroutine_Stmt ), fp2003.Prefix )
            attributes = ''
            if prefix:
                attributes = prefix.children[0].string.lower()
            scope = extract_module_scope(node)
            s = extract_module_scopes(node, "public")
            for i in s:
                if name == i:
                    scope = "public"
            s = extract_module_scopes(node, "private")
            for i in s:
                if name == i:
                    scope = "private"
            fortran_data['subroutines'].append({
                'name': name,
                'doc': docstring,
                'args': args,
                'attributes': attributes,
                'scope': scope,
            })
        
        # Collect functions
        if isinstance(node, Function_Subprogram):
            name = get_child( get_child( node , fp2003.Function_Stmt ), fp2003.Name ).string
            content = get_child( node , fp2003.Specification_Part ).content
            docstring = extract_comments( content[0].children , docmarker)
            args = extract_arguments( content[1:], docmarker )
            prefix = get_child( get_child( node , fp2003.Function_Stmt ), fp2003.Prefix )
            attributes = ''
            if prefix:
                attributes = prefix.children[0].string.lower()
            result_var = get_child( get_child( get_child( node , fp2003.Function_Stmt ), fp2003.Suffix ) , fp2003.Name ).string
            scope = extract_module_scope(node)
            s = extract_module_scopes(node, "public")
            for i in s:
                if name == i:
                    scope = "public"
            s = extract_module_scopes(node, "private")
            for i in s:
                if name == i:
                    scope = "private"
            fortran_data['functions'].append({
                'name': name,
                'doc': docstring,
                'args': args,
                'result': result_var,
                'attributes': attributes,
                'scope':scope,
            })

        # Collect derived types
        if isinstance(node, Derived_Type_Def):
            content = node.content
            docstring = extract_comments( content , docmarker)
            members, procedures = extract_derived_type( node )
            derived_type_name = get_child( get_child( node, fp2003.Derived_Type_Stmt ), fp2003.Type_Name ).string
            scope = extract_module_scope(node)
            fortran_data['types'].append({
                'name': derived_type_name,
                'doc': docstring,
                'members': members,
                'procedures': procedures,
                'scope':scope
            })

    return fortran_data

def extract_module_scope(node):
    """
    Get the scope of the module i.e. public or private.
    """
    scope = "public"
    stmt = get_child(node , fp2003.Specification_Part)
    for child in stmt.children:
        print(child.children)
        if isinstance(child, fp2003.Access_Stmt):
            if child.children[1] is None:
                scope = child.children[0].lower()
    return scope


def extract_module_scopes(node, what):
    """
    Parse the explicit public or private access statements.
    """
    access_stmt = []
    stmt = get_child( node , fp2003.Specification_Part )
    for child in stmt.children:
        if isinstance(child, fp2003.Access_Stmt):
            if (child.children[0].lower().startswith(what)) and (child.children[1] is None):
                value = child.children[1].string
                access_stmt.append(value)
    return access_stmt


def extract_comments(node, docmarker:str="!>"):
    """
    Recover docstrings from Comment nodes
    """
    doc_lines = []
    for child in node:
        if isinstance(child, fp2003.Comment):
            if child.children[0].startswith(docmarker):
                # multi-line docstring
                # empty lines are replaced by \n
                c = child.children[0][2:].strip()
                if len(c) == 0:
                    doc_lines.append("\n")
                else:
                    doc_lines.append(child.children[0][2:].strip())
    return " ".join(doc_lines) if doc_lines else None

def extract_arguments(list, docmarker:str="!>"):
    """
    
    """
    args_doc = {}
    for idx in range(0,len(list)//2):
        docs = extract_comments( list[2*idx+1].children, docmarker)
        intrinsic_type = get_child( list[2*idx] , fp2003.Intrinsic_Type_Spec ).string
        Attr_List = get_child( list[2*idx] , fp2008.Attr_Spec_List )
        attrs = intrinsic_type
        if Attr_List:
            attrs = intrinsic_type + ', ' + Attr_List.string
        Entity_List = get_child( list[2*idx] , fp2003.Entity_Decl_List )
        for arg in Entity_List.children:
            args_doc[arg.string] = {
                    'description': docs,
                    'attributes': attrs # attributes
                }
    return args_doc

def extract_derived_type(node):
    """
    
    """
    members = []
    procedures = []

    components = get_child( node , fp2003.Component_Part )
    for component in components.children:
        attribute = get_child( component , fp2003.Intrinsic_Type_Spec ).string
        attr_spec_list = get_child( component , fp2008.Component_Attr_Spec_List )
        if attr_spec_list:
            Attr = get_child( attr_spec_list, fp2003.Component_Attr_Spec ).string
            attribute = attribute + ', ' + Attr.lower()
        name = get_child(get_child(get_child( 
               component , fp2003.Component_Decl_List ), 
               fp2003.Component_Decl ),
               fp2003.Name ).string
        members.append({
                    'name': name,
                    'attributes': attribute
                })
        
    type_Bound_procedures = get_child( node , fp2003.Type_Bound_Procedure_Part )
    # TODO: unroll Specific_Binding and Generic_Binding
     
    return members, procedures



