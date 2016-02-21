# -*- coding: utf-8 -*-
from datetime import datetime

from bs4 import BeautifulSoup
from git import InvalidGitRepositoryError, Repo
from mock import ANY, call, Mock

from nose.tools import (
    assert_equal,
    assert_greater,
    assert_less_equal,
    assert_in,
    assert_not_in,
    assert_raises,
)

from . import TempDirTestCase
from sphinx_git import GitChangelog


class TestableGitChangelog(GitChangelog):

    def __init__(self):
        self.lineno = 123
        self.options = {}
        self.state = Mock()


class ChangelogTestCase(TempDirTestCase):

    def setup(self):
        super(ChangelogTestCase, self).setup()
        self.changelog = TestableGitChangelog()
        self.changelog.state.document.settings.env.srcdir = self.root


class TestNoRepository(ChangelogTestCase):

    def test_not_a_repository(self):
        assert_raises(InvalidGitRepositoryError, self.changelog.run)


class TestWithRepository(ChangelogTestCase):

    def _set_username(self, username):
        config_writer = self.repo.config_writer()
        config_writer.set_value('user', 'name', username)
        config_writer.release()

    def setup(self):
        super(TestWithRepository, self).setup()
        self.repo = Repo.init(self.root)
        self._set_username('Test User')

    def test_no_commits(self):
        assert_raises(ValueError, self.changelog.run)

    def test_single_commit_produces_single_item(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(1, len(l.findAll('list_item')))

    def test_single_commit_message_and_user_display(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(5, len(children))
        assert_equal('my root commit', children[0].text)
        assert_equal('Test User', children[2].text)

    def test_single_commit_message_and_user_display_with_non_ascii_chars(self):
        self._set_username('þéßþ  Úßéë')
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(5, len(children))
        assert_equal('my root commit', children[0].text)
        assert_equal(u'þéßþ  Úßéë', children[2].text)

    def test_single_commit_time_display(self):
        self.repo.index.commit('my root commit')
        before = datetime.now().replace(microsecond=0)
        nodes = self.changelog.run()
        after = datetime.now()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        timestamp = datetime.strptime(children[4].text, '%Y-%m-%d %H:%M:%S')
        assert_less_equal(before, timestamp)
        assert_greater(after, timestamp)

    def test_single_commit_default_detail_setting(self):
        self.repo.index.commit(
            'my root commit\n\nadditional information\nmore info'
        )
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(6, len(children))
        assert_equal('my root commit', children[0].text)
        assert_equal('Test User', children[2].text)
        assert_equal(
            str(children[5]),
            '<paragraph>additional information\nmore info</paragraph>'
        )

    def test_single_commit_preformmated_detail_lines(self):
        self.repo.index.commit(
            'my root commit\n\nadditional information\nmore info'
        )
        self.changelog.options = {'detailed-message-pre': True}
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(6, len(children))
        assert_equal(
            str(children[5]),
            '<literal_block xml:space="preserve">additional information\n'
            'more info</literal_block>'
        )

    def test_more_than_ten_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(10, len(l.findAll('list_item')))
        for n, child in zip(range(15, 5), l.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #4', l.text)

    def test_specifying_number_of_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        self.changelog.options = {'revisions': 5}
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        l = list_markup.bullet_list
        assert_equal(5, len(l.findAll('list_item')))
        for n, child in zip(range(15, 10), l.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #9', l.text)

    def test_specifying_a_rev_list(self):
        self.repo.index.commit('before tag')
        commit = self.repo.index.commit('at tag')
        self.repo.index.commit('after tag')
        self.repo.index.commit('last commit')
        self.repo.create_tag('testtag', commit)

        self.changelog.options = {'rev-list': 'testtag..'}
        nodes = self.changelog.run()

        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))

        l = list_markup.bullet_list
        assert_equal(2, len(l.findAll('list_item')))

        children = list(l.childGenerator())
        first_element = children[0]
        second_element = children[1]
        assert_in('last commit', first_element.text)
        assert_in('after tag', second_element.text)

    def test_warning_given_if_rev_list_and_revisions_both_given(self):
        self.repo.index.commit('a commit')
        self.changelog.options = {'rev-list': 'HEAD', 'revisions': 12}
        nodes = self.changelog.run()
        assert_equal(
            1, self.changelog.state.document.reporter.warning.call_count
        )

    def test_line_number_displayed_in_multiple_option_warning(self):
        self.repo.index.commit('a commit')
        self.changelog.options = {'rev-list': 'HEAD', 'revisions': 12}
        nodes = self.changelog.run()
        document_reporter = self.changelog.state.document.reporter
        assert_equal(
            [call(ANY, line=self.changelog.lineno)],
            document_reporter.warning.call_args_list
        )
