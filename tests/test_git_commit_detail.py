# -*- coding: utf-8 -*-
import os
from tempfile import mkstemp

from bs4 import BeautifulSoup
from git import Repo
from nose.tools import assert_equal, assert_in, assert_is, assert_is_not

from sphinx_git import GitCommitDetail

from . import MakeTestableMixin, TempDirTestCase


class TestableGitCommitDetail(MakeTestableMixin, GitCommitDetail):
    github_nonce_url = 'https://github.com/no_user/no_repo.git/'
    github_nonce_commit_base = 'https://github.com/no_user/no_repo/commit/'


class TestCommitDetail(TempDirTestCase):
    def setup(self):
        super(TestCommitDetail, self).setup()
        self.commit_detail = TestableGitCommitDetail()
        self.commit_detail.state.document.settings.env.srcdir = self.root
        self.repo = Repo.init(self.root)
        config_writer = self.repo.config_writer()
        config_writer.set_value('user', 'name', 'Test User')
        config_writer.release()

    def test_commit_only(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'commit': True}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        node_fl = node_p[0]     # field list
        node_f = node_fl[0]     # field
        assert_equal(1, len(node_fl))
        assert_equal('Commit', node_f[0].astext())
        assert_equal(
            self.repo.commit().hexsha[:GitCommitDetail.default_sha_length],
            node_f[1].astext()
        )

    def test_branch_only(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'branch': True}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        node_fl = node_p[0]     # field list
        node_f = node_fl[0]     # field
        assert_equal(1, len(node_fl))
        assert_equal('Branch', node_f[0].astext())
        assert_equal('master', node_f[1].astext())

    def test_commit_and_branch(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'commit': True, 'branch': True}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        node_fl = node_p[0]     # field list
        node_f_b = node_fl[0]     # field--branch
        node_f_c = node_fl[1]     # field--commit
        assert_equal(2, len(node_fl))
        assert_equal('Commit', node_f_c[0].astext())
        assert_equal('Branch', node_f_b[0].astext())

    def test_github_link(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'commit': True}
        self.repo.create_remote('origin', self.commit_detail.github_nonce_url)
        nodes = self.commit_detail.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_is_not(list_markup.reference, None)
        assert_equal(
            self.commit_detail.github_nonce_commit_base +
            self.repo.commit().hexsha,
            list_markup.reference['refuri']
        )
        assert_equal(
            self.repo.commit().hexsha[:GitCommitDetail.default_sha_length],
            list_markup.reference.text
        )

    def test_no_github_link(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'commit': True, 'no_github_link': True}
        self.repo.create_remote('origin', self.commit_detail.github_nonce_url)
        nodes = self.commit_detail.run()
        list_markup = BeautifulSoup(str(nodes[0]), features='xml')
        assert_is(list_markup.reference, None)

    def test_sha_length(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'commit': True, 'sha_length': 4}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        node_fl = node_p[0]     # field list
        node_f = node_fl[0]     # field
        assert_equal(1, len(node_fl))
        assert_equal('Commit', node_f[0].astext())
        assert_equal(self.repo.commit().hexsha[:4], node_f[1].astext())

    def test_untracked_files(self):
        self.repo.index.commit('my root commit')
        self.commit_detail.options = {'untracked': True}
        fd, name = mkstemp(dir=self.root)
        os.close(fd)
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        assert_equal(2, len(node_p))
        node_w = node_p[1]      # nodes.warning
        node_i = node_w[0]      # inline
        assert_in('untracked', node_i.astext())

    def test_uncommitted_changes(self):
        fd, name = mkstemp(dir=self.root)
        self.repo.index.add([name])
        self.repo.index.commit('my root commit')
        os.write(fd, "some change".encode('utf-8'))
        os.close(fd)
        self.commit_detail.options = {'uncommitted': True}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        assert_equal(2, len(node_p))
        node_w = node_p[1]      # nodes.warning
        node_i = node_w[0]      # inline
        assert_in('uncommitted', node_i.astext())

    def test_detached_head(self):
        self.repo.index.commit('my root commit')
        self.repo.index.commit('a second commit')
        self.repo.head.reference = self.repo.commit('HEAD~')
        assert self.repo.head.is_detached, "HEAD unexpectedly attached"

        self.commit_detail.options = {'commit': True}
        nodes = self.commit_detail.run()
        node_p = nodes[0]       # <p> node
        node_fl = node_p[0]     # field list
        node_f = node_fl[0]     # field
        assert_equal(1, len(node_fl))
        assert_equal('Commit', node_f[0].astext())
        assert_equal(
            self.repo.commit().hexsha[:GitCommitDetail.default_sha_length],
            node_f[1].astext()
        )
