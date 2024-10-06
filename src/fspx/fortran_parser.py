import re
from fparser.common.readfortran import FortranFileReader
from fparser.two.parser import ParserFactory
from fparser.two.utils import walk
from fparser.two.Fortran2003 import Module_Stmt, Subroutine_Stmt, Function_Stmt, Derived_Type_Stmt

# Initialize Fortran 2008 parser
parser = ParserFactory().create(std="f2008")

def parse_fortran_file(file_path):
    """
    Parse a Fortran file and extract the code structure (modules, subroutines, functions, types),
    including docstrings and argument descriptions from inline comments.
    """
    docstring = None
    fortran_data = {
        'modules': [],
        'subroutines': [],
        'functions': [],
        'types': []
    }
    
    with open(file_path, 'r') as f:
        reader = FortranFileReader(f.name)
        parse_tree = parser(reader)

        # Read the file line-by-line for docstring extraction
        lines = f.readlines()

    # Walk through the AST and associate constructs with docstrings
    for stmt in walk(parse_tree):
        stmt_class = type(stmt).__name__

        # Collect modules
        if isinstance(stmt, Module_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            fortran_data['modules'].append({
                'name': str(stmt.children[1]),
                'doc': docstring
            })

        # Collect subroutines
        elif isinstance(stmt, Subroutine_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            args = extract_argument_docstrings(lines, stmt)
            fortran_data['subroutines'].append({
                'name': str(stmt.children[1]),
                'doc': docstring,
                'args': args
            })

        # Collect functions
        elif isinstance(stmt, Function_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            args = extract_argument_docstrings(lines, stmt)
            fortran_data['functions'].append({
                'name': str(stmt.children[1]),
                'doc': docstring,
                'args': args
            })

        # Collect derived types
        elif isinstance(stmt, Derived_Type_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            fortran_data['types'].append({
                'name': str(stmt.children[1]),
                'doc': docstring
            })

    return fortran_data

def extract_inline_comment(lines, line_num):
    """
    Extract a docstring from the line above a Fortran statement if it starts with !>.
    """
    if line_num < 0 or line_num >= len(lines):
        return None  # Out of bounds check

    comment_line = lines[line_num].strip()

    if comment_line.startswith('!>'):
        return comment_line[2:].strip()  # Remove the !> marker
    return None

def extract_docstring(comment_lines):
    """
    Extract docstrings from a list of comment lines.
    Only lines starting with !> are considered part of the docstring.
    """
    doc_lines = []
    for line in comment_lines:
        stripped_line = line.strip()
        if stripped_line.startswith('!>'):
            # Remove the !> marker and any leading/trailing whitespace
            doc_lines.append(stripped_line[2:].strip())

    return "\n".join(doc_lines) if doc_lines else None


def extract_argument_docstrings(lines, stmt):
    """
    Extract argument descriptions (docstrings) and attributes for subroutine/function arguments
    from the Fortran source code.

    1. Extract arguments from the subroutine or function signature.
    2. Match the arguments with their type, intent, and attributes declared in subsequent lines.
    """
    import re
    args_doc = {}
    
    # Extract the list of arguments from the subroutine/function definition line
    match = re.search(r'\((.*?)\)', stmt.item.line.strip())
    if not match:
        return args_doc  # No arguments found, return empty dictionary
    
    arg_list = match.group(1).split(',')
    arg_list = [arg.strip() for arg in arg_list if arg.strip()]  # Clean up whitespace
    
    # Now parse the subsequent lines to find the type, intent, and any inline comment for each argument
    for line in lines:
        line = line.strip()

        # Match a line like: "type(kind), intent(in) :: variable_name"
        match = re.search(r'::\s*(\w+)', line)
        if match:
            arg_name = match.group(1)

            # Check if this argument is in the subroutine/function argument list
            if arg_name in arg_list:
                # Extract the attributes from the part before "::"
                attributes = line.split("::")[0].strip()
                
                # Extract any inline comment following the argument declaration
                comment_match = re.search(r'!>(.*)$', line)
                arg_doc = comment_match.group(1).strip() if comment_match else "No description provided."
                
                # Store both the description and attributes
                args_doc[arg_name] = {
                    'description': arg_doc,
                    'attributes': attributes
                }
    
    return args_doc
