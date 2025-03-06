r"""Parse Fortran code with FORD as backend."""

from ford.sourceform import ProjectSettings
from ford.sourceform import FortranModule, FortranSubmodule
from ford.sourceform import FortranSourceFile, FortranSubroutine, FortranFunction, FortranBase, FortranType, FortranVariable

def get_fargs(f: FortranFunction | FortranSubroutine):
    r"""Return the description of the arguments."""
    args = {}
    f.attribs
    for i in f.args:
        args[i.name] = {"description": "\n".join(i.doc_list), "attributes": i.full_declaration}
        if i.parameter:
            args[i.name]["attributes"] += f", parameter"
        if i.intent:
            args[i.name]["attributes"] += f", intent({i.intent:s})"
        if i.optional:
            args[i.name]["attributes"] += f", optional"

    return args

def get_fresult_as_arg(f: FortranFunction):
    r"""Return the result."""
    ret={}
    i = f.retvar
    ret[i.name] = {"description": "", "attributes": i.full_declaration}
    return ret

def get_fresult(f: FortranFunction):
    r"""Return the result name."""
    if f.name == f.retvar.name:
        return ""
    else:
        return f.retvar.name

def get_doc(item: FortranBase):
    r"""Return the doc."""
    doc = []
    for i in item.doc_list:
        if len(i.strip()) == 0:
            doc.append("\n")
        else:
            doc.append(i)
    return "".join(doc)

def get_type_members(item: FortranType):
    r"""Return the members."""
    members = []
    for i in item.variables:
        d = {"name": i.name, "attributes": i.full_declaration}
        members.append(d)
    return members

def get_type_procedures(item: FortranType):
    r"""Return the procedures."""
    procedures = []
    for i in item.boundprocs:
        d = {"name": i.name, "attributes": i.full_declaration}
        procedures.append(d)
    return procedures

def parse_fortran_file(file_path, docmarker:str="!*>|"):
    r"""Parse Fortran code."""
     
    settings = ProjectSettings(file_path)
    if docmarker:
        if len(docmarker) == 4:
            docmark, docmark_alt, predocmark, predocmark_alt = docmarker
            settings = ProjectSettings(docmark=docmark, 
                           docmark_alt=docmark_alt, 
                           predocmark=predocmark, 
                           predocmark_alt=predocmark_alt)
        else:
            raise ValueError("docmarker must a be an string of 4 characters defining the docmarker, docmarker_alt, predocmark, predocmark_alt.")
    
    reader = FortranSourceFile(file_path, settings=settings)

    fortran_data = {
        'modules': [],
        'submodules': [],
        'subroutines': [],
        'functions': [],
        'types': []
    }
    for i in reader.markdownable_items:
        if isinstance(i, FortranModule):
            fortran_data["modules"].append(
                {"name": i.name,
                 "doc": get_doc(i),
                 "permission": i.permission
                }
            )

        if isinstance(i, FortranSubmodule):
            fortran_data["submodules"].append({
                "name": i.name,
                "doc": get_doc(i),
                "permission": i.permission
            }
            )

        if isinstance(i, FortranFunction):
            args = get_fargs(i)
            ret = get_fresult(i)
            ret_arg = get_fresult_as_arg(i)
            args.update(ret_arg)
            attribs = " ".join(i.attribs)
            if ret == "":
                attribs = i.retvar.vartype + " " + attribs
            fortran_data["functions"].append(
                {
                    "name": i.name,
                    "args": args,
                    "doc": get_doc(i),
                    "result": get_fresult(i),
                    "attributes": attribs,
                    "permission": i.permission
                }
            )
        
        if isinstance(i, FortranSubroutine):
            args = get_fargs(i)
            fortran_data["subroutines"].append(
                {
                    "name": i.name,
                    "args": args,
                    "doc": get_doc(i),
                    "result": "",
                    "attributes": " ".join(i.attribs),
                    "permission": i.permission
                }
            )

        if isinstance(i, FortranType):
            fortran_data["types"].append({
                "name":i.name, 
                "doc": get_doc(i),
                "permission": i.permission,
                "members": get_type_members(i),
                "procedures": get_type_procedures(i)
            }
        )


    return fortran_data
