from shutil import rmtree
from tempfile import mkdtemp

from git import InvalidGitRepositoryError, Repo
from mock import Mock
from nose.tools import assert_equal, assert_in, assert_not_in, assert_raises

from sphinx_git import GitChangelog


class TestableGitChangelog(GitChangelog):

    def __init__(self):
        self.state = Mock()


class TempDirTestCase(object):

    def setup(self):
        self.root = mkdtemp()
        self.changelog = TestableGitChangelog()
        self.changelog.state.document.settings.env.srcdir = self.root

    def teardown(self):
        rmtree(self.root)


class TestNoRepository(TempDirTestCase):

    def test_not_a_repository(self):
        assert_raises(InvalidGitRepositoryError, self.changelog.run)


class TestWithRepository(TempDirTestCase):

    def setup(self):
        super(TestWithRepository, self).setup()
        self.repo = Repo.init(self.root)

    def test_no_commits(self):
        assert_raises(ValueError, self.changelog.run)

    def test_single_commit(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_node = nodes[0]
        assert_equal(1, len(list_node))
        list_markup = str(list_node)
        assert_in('<bullet_list>', list_markup)
        assert_in('my root commit', list_markup)

    def test_more_than_ten_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_node = nodes[0]
        assert_equal(10, len(list_node))
        list_markup = str(list_node)
        assert_in('<bullet_list>', list_markup)
        for n in range(5, 15):
            assert_in('commit #{0}'.format(n), list_markup)
        assert_not_in('commit #4', list_markup)
