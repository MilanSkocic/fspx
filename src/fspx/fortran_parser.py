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
            attributes = extract_procedure_attributes(stmt.item.line)
            fortran_data['subroutines'].append({
                'name': str(stmt.children[1]),
                'doc': docstring,
                'args': args,
                'attributes': attributes
            })

        # Collect functions
        elif isinstance(stmt, Function_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            args = extract_argument_docstrings(lines, stmt)
            attributes = extract_procedure_attributes(stmt.item.line)
            # Extract the "result" clause if present
            result_match = re.search(r'result\((\w+)\)', stmt.item.line)
            result_var = None
            if result_match:
                result_var_name = result_match.group(1)
                # Get the result variable's attributes and description
                result_var = extract_result_attributes(lines[stmt.item.span[0]-1:], result_var_name)
                result_var['name'] = result_var_name  # Add the name of the result variable

            fortran_data['functions'].append({
                'name': str(stmt.children[1]),
                'doc': docstring,
                'args': args,
                'result': result_var,  # Pass the result variable to the function data
                'attributes': attributes
            })

        # Collect derived types
        elif isinstance(stmt, Derived_Type_Stmt):
            docstring = extract_inline_comment(lines, stmt.item.span[0])
            derived_type_name = str(stmt.children[1])
            members, procedures = extract_derived_type_members_and_procedures(lines, stmt.item.span[0])
            fortran_data['types'].append({
                'name': derived_type_name,
                'doc': docstring,
                'members': members,
                'procedures': procedures
            })
            

    return fortran_data

def extract_inline_comment(lines, line_num):
    """
    Extract a docstring from the line above a Fortran statement if it starts with !>.
    """
    if line_num < 0 or line_num >= len(lines):
        return None  # Out of bounds check

    return extract_docstring(lines[line_num:])

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
        else:
            break

    return " ".join(doc_lines) if doc_lines else None


def extract_argument_docstrings(lines, stmt):
    """
    Extract argument descriptions (docstrings) and attributes for subroutine/function arguments
    from the Fortran source code. The result variable in Fortran functions will be handled separately.
    """
    args_doc = {}
    
    # Extract the list of arguments from the subroutine/function definition line (ignoring result variable)
    match = re.search(r'\((.*?)\)', stmt.item.line.strip())
    if not match:
        return args_doc  # No arguments found, return empty dictionary
    
    arg_list = match.group(1).split(',')
    arg_list = [arg.strip() for arg in arg_list if arg.strip()]  # Clean up whitespace
    
    # Parse subsequent lines for type, intent, and inline comments for each argument
    for line in lines:
        line = line.strip()
        
        # Match a line like: "type(kind), intent(in) :: variable_name"
        match = re.search(r'::\s*(\w+)', line)
        if match:
            arg_name = match.group(1)

            # Check if this argument is in the argument list (ignore result variable here)
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


def extract_result_attributes(lines, result_var):
    """
    Extract the attributes and description for the result variable in a Fortran function.
    Look for its declaration in the subsequent lines and return the type and attributes.
    """
    for line in lines:
        line = line.strip()

        # Look for a line like: "type(kind), intent(out) :: result_var"
        if result_var in line and '::' in line:
            # Extract the attributes from the part before "::"
            attributes = line.split("::")[0].strip()

            # Extract any inline comment following the result variable declaration
            comment_match = re.search(r'!>(.*)$', line)
            description = comment_match.group(1).strip() if comment_match else "No description provided."
            
            # Return both the attributes and description
            return {
                'description': description,
                'attributes': attributes
            }

    # Default return value if no specific declaration found
    return {
        'description': "No description provided.",
        'attributes': "Unknown"
    }

def extract_derived_type_members_and_procedures(lines, start_line):
    """
    Extract the members and type-bound procedures of a derived type.
    """
    members = []
    procedures = []
    inside_contains = False

    for i, line in enumerate(lines[start_line:], start=start_line):
        stripped_line = line.strip()

        # Detect the "contains" statement, which marks the start of type-bound procedures
        if stripped_line.lower() == "contains":
            inside_contains = True
            continue

        if inside_contains:
            # We are now processing type-bound procedures
            procedure_match = re.match(r'\s*(procedure)\s*::\s*(\w+)', stripped_line)
            if procedure_match:
                procedures.append({
                    'name': procedure_match.group(2),
                    'attributes': procedure_match.group(1)
                })
        else:
            # We are processing derived type members
            member_match = re.match(r'\s*(\w+)\s*::\s*(\w+)', stripped_line)
            if member_match:
                members.append({
                    'name': member_match.group(2),
                    'attributes': member_match.group(1)
                })

    return members, procedures

def extract_procedure_attributes(line):
    """
    Extract attributes such as 'pure', 'elemental', 'recursive' from a subroutine or function declaration line.
    """
    attributes = []
    if "pure" in line:
        attributes.append("pure")
    if "elemental" in line:
        attributes.append("elemental")
    if "recursive" in line:
        attributes.append("recursive")
    return ", ".join(attributes) if attributes else None