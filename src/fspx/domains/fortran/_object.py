"""Fortran Objects."""
from docutils import nodes
from sphinx.util.docfields import Field

class FortranField(Field):
    def make_xref(self, rolename, domain, target, innernode=nodes.emphasis,
                  modname=None, typename=None):
        if not rolename:
            return innernode(target, target)
        refnode = addnodes.pending_xref(
            '',
            refdomain=domain,
            refexplicit=False,
            reftype=rolename,
            reftarget=target,
            modname=modname,
            typename=typename)
        refnode += innernode(target, target)
        return refnode


class FortranCallField(FortranField):
    is_grouped = True

    def __init__(self, name, names=(), label=None, rolename=None):
        Field.__init__(self, name, names, label, True, rolename)

    def make_field(self, types, domain, items, **kwargs):

        fieldname = nodes.field_name('', self.label)
        #par = Field.make_field(self, types, domain, items[0])
        par = nodes.paragraph()
        for i, item in enumerate(items):
            if i:
                par += nodes.Text(' ')
            par += item[1]  # Field.make_field(self, types, domain, item)
        fieldbody = nodes.field_body('', par)
        return nodes.field('', fieldname, fieldbody)
