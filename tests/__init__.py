from shutil import rmtree
from tempfile import mkdtemp

from mock import Mock


class TempDirTestCase(object):
    def setup(self):
        self.root = mkdtemp()

    def teardown(self):
        rmtree(self.root)


class MakeTestableMixin(object):
    """
    Define an __init__ with no arguments for sphinx directives.

    This saves us from having to pass in a bunch of Mocks which we will never
    look at.
    """

    def __init__(self):
        self.lineno = 123
        self.options = {}
        self.state = Mock()
