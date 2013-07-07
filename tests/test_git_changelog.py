from datetime import datetime
from shutil import rmtree
from tempfile import mkdtemp

from BeautifulSoup import BeautifulStoneSoup
from git import InvalidGitRepositoryError, Repo
from mock import Mock

from tests.assertions import (
    assert_equal,
    assert_greater,
    assert_less_equal,
    assert_in,
    assert_not_in,
    assert_raises,
)

from sphinx_git import GitChangelog


class TestableGitChangelog(GitChangelog):

    def __init__(self):
        self.options = {}
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
        self.repo.config_writer().set_value('user', 'name', 'Test User')

    def test_no_commits(self):
        assert_raises(ValueError, self.changelog.run)

    def test_single_commit_produces_single_item(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(1, len(l.findAll('list_item')))

    def test_single_commit_message_and_user_display(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(5, len(children))
        assert_equal('my root commit', children[0].text)
        assert_equal('Test User', children[2].text)

    def test_single_commit_time_display(self):
        self.repo.index.commit('my root commit')
        before = datetime.now().replace(microsecond=0)
        nodes = self.changelog.run()
        after = datetime.now()
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        timestamp = datetime.strptime(children[4].text, '%Y-%m-%d %H:%M:%S')
        assert_less_equal(before, timestamp)
        assert_greater(after, timestamp)

    def test_single_commit_multiple_lines(self):
        self.repo.index.commit('my root commit\n\nadditional information')
        nodes = self.changelog.run()
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(6, len(children))
        assert_equal('my root commit', children[0].text)
        assert_equal('Test User', children[2].text)
        assert_equal(str(children[5]),
                     '<caption>additional information</caption>')

    def test_more_than_ten_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(10, len(l.findAll('list_item')))
        for n, child in zip(range(15, 5), l.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #4', l.text)

    def test_specifying_number_of_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        self.changelog.options = {'revisions': '5'}
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulStoneSoup(str(nodes[0]))
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(5, len(l.findAll('list_item')))
        for n, child in zip(range(15, 10), l.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #9', l.text)
