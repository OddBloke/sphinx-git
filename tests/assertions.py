import re

import unittest2


caps = re.compile('([A-Z])')


def pep8(name):
    return caps.sub(lambda m: '_' + m.groups()[0].lower(), name)


class Dummy(unittest2.TestCase):
    def nop():
        pass
_t = Dummy('nop')


for at in [at for at in dir(_t) if
           at.startswith('assert') and not '_' in at]:
    pepd = pep8(at)
    vars()[pepd] = getattr(_t, at)

del Dummy
del _t
del pep8
