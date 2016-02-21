from shutil import rmtree
from tempfile import mkdtemp


class TempDirTestCase(object):
    def setup(self):
        self.root = mkdtemp()

    def teardown(self):
        rmtree(self.root)
