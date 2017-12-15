import os
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from git import Repo

from nose.tools import (
    assert_equal,
)

from . import MakeTestableMixin, TempDirTestCase
from sphinx_git import GitChangelogByDate


class TestableGitChangelogByDate(MakeTestableMixin, GitChangelogByDate):

    pass


class ChangelogByDateTestCase(TempDirTestCase):

    def _set_username(self, username):
        config_writer = self.repo.config_writer()
        config_writer.set_value('user', 'name', username)
        config_writer.release()

    def setup(self):
        super(ChangelogByDateTestCase, self).setup()
        self.changelog = TestableGitChangelogByDate()
        self.changelog.state.document.settings.env.srcdir = self.root
        self.repo = Repo.init(self.root)
        self._set_username('Test User')


class TestGroupByDate(ChangelogByDateTestCase):

    def test_single_commit_produces_single_item(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        # One bullet_list for the dates and one for the commits on that
        # unique date
        assert_equal(2, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        # One list_item for the date and one for the commit on that date
        assert_equal(2, len(l.findAll('list_item')))

    def test_commits_on_same_date_produce_single_item(self):
        non_root_commits_count = 5
        self.repo.index.commit('my root commit')
        for i in range(non_root_commits_count):
            self.repo.index.commit('commit #{}'.format(i+1))

        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        # One bullet_list for the dates and one for the commits on that
        # unique date
        assert_equal(2,  len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        # One list_item for the date and one per commit on that date
        assert_equal(2 + non_root_commits_count, len(l.findAll('list_item')))

    def test_commits_on_different_dates_produce_one_item_per_date(self):
        non_root_commits_count = 5
        self.repo.index.commit('my root commit')
        for i in range(non_root_commits_count):
            self.repo.index.commit('commit #{}'.format(i + 1))

        # change date
        tomorrow = '{}'.format(
            datetime.now() + timedelta(days=1)
        ).split('.')[0]
        os.environ['GIT_AUTHOR_DATE'] = tomorrow
        os.environ['GIT_COMMITER_DATE'] = tomorrow
        for i in range(non_root_commits_count):
            self.repo.index.commit('commit #{}'.format(
                i + 1 + non_root_commits_count
            ))

        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        # One bullet_list for the dates and one for the commits on each date
        assert_equal(3,  len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        # One list_item for each date and one per commit on that date
        assert_equal(2 + 2 * non_root_commits_count,
                     len(l.findAll('list_item')))
