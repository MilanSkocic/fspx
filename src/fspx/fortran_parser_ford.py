"""Parse Fortran code with FORD as backend."""

from ford.sourceform import ProjectSettings
from ford.sourceform import FortranModule, FortranSubmodule
from ford.sourceform import FortranSourceFile, FortranSubroutine, FortranFunction, FortranBase, FortranType

def get_args(f: FortranFunction | FortranSubroutine):
    args = {}
    f.attribs
    for i in f.args:
        attributes = f"{i.vartype:s}, intent({i.intent:s})"
        if i.optional:
            attributes += ", optional"
        args[i.name] = {"description": "\n".join(i.doc_list), "attributes": attributes}

    return args

def get_return_arg(f: FortranFunction):
    ret={}
    i = f.retvar
    attributes = f"{i.vartype:s}"
    ret[i.name] = {"description": "", "attributes": attributes}

    return ret

def get_func_return(f: FortranFunction):

    if f.name == f.retvar.name:
        return ""
    else:
        return f.retvar.name

def get_doc(item: FortranBase):

    doc = []
    for i in item.doc_list:
        if len(i.strip()) == 0:
            doc.append("\n")
        else:
            doc.append(i)
    return "".join(doc)

def get_members(item: FortranType):
    members = []
    for i in item.variables:
        d = {"name": i.name, "attributes": f"{i.vartype:s}"}
        members.append(d)
    return members

def parse_fortran_file(file_path, docmarker:str="!>"):

    reader = FortranSourceFile(file_path, ProjectSettings({"p":"p"}))

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
            args = get_args(i)
            ret = get_func_return(i)
            ret_arg = get_return_arg(i)
            args.update(ret_arg)
            attribs = " ".join(i.attribs)
            if ret == "":
                attribs = i.retvar.vartype + " " + attribs
            fortran_data["functions"].append(
                {
                    "name": i.name,
                    "args": args,
                    "doc": get_doc(i),
                    "result": get_func_return(i),
                    "attributes": attribs,
                    "permission": i.permission
                }
            )
        
        if isinstance(i, FortranSubroutine):
            args = get_args(i)
            fortran_data["functions"].append(
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
            print(dir(i))
            print(i.variables)
            fortran_data["types"].append({
                "name":i.name, 
                "doc": get_doc(i),
                "permission": i.permission,
                "members": get_members(i),
                "procedures": [{"name":"", "attributes": ""}]
            }
        )


    return fortran_data
