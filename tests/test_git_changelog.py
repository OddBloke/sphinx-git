from shutil import rmtree
from tempfile import mkdtemp

from git import InvalidGitRepositoryError
from mock import Mock
from nose.tools import assert_raises

from sphinx_git import GitChangelog


class TestableGitChangelog(GitChangelog):

    def __init__(self):
        self.state = Mock()


class TempDirTestCase():

    def setup(self):
        self.root = mkdtemp()
        self.changelog = TestableGitChangelog()
        self.changelog.state.document.settings.env.srcdir = self.root

    def teardown(self):
        rmtree(self.root)


class TestNoRepository(TempDirTestCase):

    def test_not_a_repository(self):
        assert_raises(InvalidGitRepositoryError, self.changelog.run)
