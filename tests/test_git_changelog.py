# -*- coding: utf-8 -*-
import os
from datetime import datetime

import six
from bs4 import BeautifulSoup
from git import InvalidGitRepositoryError, Repo
from mock import ANY, call
from nose.tools import (
    assert_equal,
    assert_greater,
    assert_in,
    assert_less_equal,
    assert_not_in,
    assert_raises,
)

from sphinx_git import GitChangelog

from . import MakeTestableMixin, TempDirTestCase


class TestableGitChangelog(MakeTestableMixin, GitChangelog):

    pass


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
        bullet_list = list_markup.bullet_list
        assert_equal(1, len(bullet_list.findAll('list_item')))

    def test_single_commit_message_and_user_display(self):
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(1, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(5, len(par_children))
        assert_equal('my root commit', par_children[0].text)
        assert_equal('Test User', par_children[2].text)

    def test_single_commit_message_and_user_display_with_non_ascii_chars(self):
        self._set_username('þéßþ  Úßéë')
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(six.text_type(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(1, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(5, len(par_children))
        assert_equal('my root commit', par_children[0].text)
        assert_equal(u'þéßþ  Úßéë', par_children[2].text)

    def test_single_commit_time_display(self):
        before = datetime.now().replace(microsecond=0)
        self.repo.index.commit('my root commit')
        nodes = self.changelog.run()
        after = datetime.now()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item.paragraph
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
        assert_equal(2, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(5, len(par_children))
        assert_equal('my root commit', par_children[0].text)
        assert_equal('Test User', par_children[2].text)
        assert_equal(
            str(children[1]),
            '<paragraph>additional information\nmore info</paragraph>'
        )

    def test_single_commit_preformmated_detail_lines(self):
        self.repo.index.commit(
            'my root commit\n\nadditional information\nmore info'
        )
        self.changelog.options.update({'detailed-message-pre': True})
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(2, len(children))
        assert_equal(
            str(children[1]),
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
        bullet_list = list_markup.bullet_list
        assert_equal(10, len(bullet_list.findAll('list_item')))
        for n, child in zip(range(15, 5), bullet_list.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #4', bullet_list.text)

    def test_specifying_number_of_commits(self):
        for n in range(15):
            self.repo.index.commit('commit #{0}'.format(n))
        self.changelog.options.update({'revisions': 5})
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))
        bullet_list = list_markup.bullet_list
        assert_equal(5, len(bullet_list.findAll('list_item')))
        for n, child in zip(range(15, 10), bullet_list.childGenerator()):
            assert_in('commit #{0}'.format(n), child.text)
        assert_not_in('commit #9', bullet_list.text)

    def test_specifying_a_rev_list(self):
        self.repo.index.commit('before tag')
        commit = self.repo.index.commit('at tag')
        self.repo.index.commit('after tag')
        self.repo.index.commit('last commit')
        self.repo.create_tag('testtag', commit)

        self.changelog.options.update({'rev-list': 'testtag..'})
        nodes = self.changelog.run()

        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))

        bullet_list = list_markup.bullet_list
        assert_equal(2, len(bullet_list.findAll('list_item')))

        children = list(bullet_list.childGenerator())
        first_element = children[0]
        second_element = children[1]
        assert_in('last commit', first_element.text)
        assert_in('after tag', second_element.text)

    def test_warning_given_if_rev_list_and_revisions_both_given(self):
        self.repo.index.commit('a commit')
        self.changelog.options.update({'rev-list': 'HEAD', 'revisions': 12})
        nodes = self.changelog.run()
        assert_equal(
            1, self.changelog.state.document.reporter.warning.call_count
        )

    def test_line_number_displayed_in_multiple_option_warning(self):
        self.repo.index.commit('a commit')
        self.changelog.options.update({'rev-list': 'HEAD', 'revisions': 12})
        nodes = self.changelog.run()
        document_reporter = self.changelog.state.document.reporter
        assert_equal(
            [call(ANY, line=self.changelog.lineno)],
            document_reporter.warning.call_args_list
        )

    def test_name_filter(self):
        self.repo.index.commit('initial')
        for file_name in ['abc.txt', 'bcd.txt', 'abc.other', 'atxt']:
            full_path = os.path.join(self.repo.working_tree_dir, file_name)
            f = open(full_path, 'w+')
            f.close()
            self.repo.index.add([full_path])
            self.repo.index.commit('commit with file {}'.format(file_name))
        self.repo.index.commit('commit without file')

        self.changelog.options.update({'filename_filter': 'a.*txt'})
        nodes = self.changelog.run()
        assert_equal(1, len(nodes))
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))

        bullet_list = list_markup.bullet_list
        assert_equal(2, len(bullet_list.findAll('list_item')), nodes)

        next_file = os.path.join(self.repo.working_tree_dir, 'atxt')
        f = open(next_file, 'w+')
        f.close()
        self.repo.index.add([next_file])
        self.repo.index.commit('show me')

        nodes = self.changelog.run()
        assert_equal(1, len(nodes), nodes)
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_equal(1, len(list_markup.findAll('bullet_list')))

        bullet_list = list_markup.bullet_list
        assert_equal(2, len(bullet_list.findAll('list_item')), nodes)

    def test_single_commit_hide_details(self):
        self.repo.index.commit(
            'Another commit\n\nToo much information'
        )
        self.changelog.options.update({'hide_details': True})
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        assert_equal(1, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(5, len(par_children))
        assert_equal('Another commit', par_children[0].text)
        assert_equal('Test User', par_children[2].text)

    def test_single_commit_message_hide_author(self):
        self.repo.index.commit('Yet another commit')
        self.changelog.options.update({'hide_author': True})
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        print(children)
        assert_equal(1, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(3, len(par_children))
        assert_equal('Yet another commit', par_children[0].text)
        assert_not_in(' by Test User', par_children[1].text)
        assert_in(' at ', par_children[1].text)

    def test_single_commit_message_hide_date(self):
        self.repo.index.commit('Yet yet another commit')
        self.changelog.options.update({'hide_date': True})
        nodes = self.changelog.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        item = list_markup.bullet_list.list_item
        children = list(item.childGenerator())
        print(children)
        assert_equal(1, len(children))
        par_children = list(item.paragraph.childGenerator())
        assert_equal(3, len(par_children))
        assert_equal('Yet yet another commit', par_children[0].text)
        assert_not_in(' at ', par_children[1].text)
        assert_in(' by ', par_children[1].text)


class TestWithOtherRepository(TestWithRepository):
    """
    The destination repository is not in the same repository as the rst files.
    """
    def setup(self):
        super(TestWithOtherRepository, self).setup()
        self.changelog.state.document.settings.env.srcdir = os.getcwd()
        self.changelog.options.update({'repo-dir': self.root})
