# Copyright 2012-2013 (C) Daniel Watkins <daniel@daniel-watkins.co.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from datetime import datetime

import six
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from git import Repo


# pylint: disable=too-few-public-methods, abstract-method
class GitDirectiveBase(Directive):
    def _find_repo(self):
        env = self.state.document.settings.env
        repo_dir = self.options.get('repo-dir', env.srcdir)
        repo = Repo(repo_dir, search_parent_directories=True)
        return repo


# pylint: disable=too-few-public-methods
class GitCommitDetail(GitDirectiveBase):
    default_sha_length = 7

    option_spec = {
        'branch': bool,
        'commit': bool,
        'uncommitted': bool,
        'untracked': bool,
        'sha_length': int,
        'no_github_link': bool,
    }

    # pylint: disable=attribute-defined-outside-init
    def run(self):
        self.repo = self._find_repo()
        self.branch_name = None
        if not self.repo.head.is_detached:
            self.branch_name = self.repo.head.ref.name
        self.commit = self.repo.commit()
        self.sha_length = self.options.get('sha_length',
                                           self.default_sha_length)
        markup = self._build_markup()
        return markup

    def _build_markup(self):
        field_list = nodes.field_list()
        item = nodes.paragraph()
        item.append(field_list)
        if 'branch' in self.options and self.branch_name is not None:
            name = nodes.field_name(text="Branch")
            body = nodes.field_body()
            body.append(nodes.emphasis(text=self.branch_name))
            field = nodes.field()
            field += [name, body]
            field_list.append(field)
        if 'commit' in self.options:
            name = nodes.field_name(text="Commit")
            body = nodes.field_body()
            if 'no_github_link' in self.options:
                body.append(self._commit_text_node())
            else:
                body.append(self._github_link())
            field = nodes.field()
            field += [name, body]
            field_list.append(field)
        if 'uncommitted' in self.options and self.repo.is_dirty():
            item.append(nodes.warning('', nodes.inline(
                text="There were uncommitted changes when this was compiled."
            )))
        if 'untracked' in self.options and self.repo.untracked_files:
            item.append(nodes.warning('', nodes.inline(
                text="There were untracked files when this was compiled."
            )))
        return [item]

    def _github_link(self):
        try:
            url = self.repo.remotes.origin.url
            url = url.replace('.git/', '').replace('.git', '')
            if 'github' in url:
                commit_url = url + '/commit/' + self.commit.hexsha
                ref = nodes.reference('', self.commit.hexsha[:self.sha_length],
                                      refuri=commit_url)
                par = nodes.paragraph('', '', ref)
                return par
            return self._commit_text_node()
        except AttributeError as error:
            print("ERROR: ", error)
            return self._commit_text_node()

    def _commit_text_node(self):
        return nodes.emphasis(text=self.commit.hexsha[:self.sha_length])


# pylint: disable=too-few-public-methods
class GitChangelog(GitDirectiveBase):

    option_spec = {
        'revisions': directives.nonnegative_int,
        'rev-list': six.text_type,
        'detailed-message-pre': bool,
        'detailed-message-strong': bool,
        'filename_filter': six.text_type,
        'hide_author': bool,
        'hide_date': bool,
        'hide_details': bool,
        'repo-dir': six.text_type,
    }

    def run(self):
        if 'rev-list' in self.options and 'revisions' in self.options:
            self.state.document.reporter.warning(
                'Both rev-list and revisions options given; proceeding using'
                ' only rev-list.',
                line=self.lineno
            )
        commits = self._commits_to_display()
        markup = self._build_markup(commits)
        return markup

    def _commits_to_display(self):
        repo = self._find_repo()
        commits = self._filter_commits(repo)
        return commits

    def _filter_commits(self, repo):
        if 'rev-list' in self.options:
            commits = repo.iter_commits(rev=self.options['rev-list'])
        else:
            commits = repo.iter_commits()
            revisions_to_display = self.options.get('revisions', 10)
            commits = list(commits)[:revisions_to_display]
        if 'filename_filter' in self.options:
            return self._filter_commits_on_filenames(commits)
        return commits

    def _filter_commits_on_filenames(self, commits):
        filtered_commits = []
        filter_exp = re.compile(self.options.get('filename_filter', r'.*'))
        for commit in commits:
            # SHA of an empty tree found at
            # http://stackoverflow.com/questions/33916648/get-the-diff-details-of-first-commit-in-gitpython
            # will be used to get the list of files of initial commit
            compared_with = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
            if len(commit.parents) > 0:  # pylint: disable=len-as-condition
                compared_with = commit.parents[0].hexsha
            for diff in commit.diff(compared_with):
                if filter_exp.match(diff.a_path) or \
                        filter_exp.match(diff.b_path):
                    filtered_commits.append(commit)
                    break
        return filtered_commits

    def _build_markup(self, commits):
        list_node = nodes.bullet_list()
        for commit in commits:
            date_str = datetime.fromtimestamp(commit.authored_date)
            if '\n' in commit.message:
                message, detailed_message = commit.message.split('\n', 1)
            else:
                message = commit.message
                detailed_message = None

            item = nodes.list_item()
            par = nodes.paragraph()
            # choose detailed message style by detailed-message-strong option
            if self.options.get('detailed-message-strong', True):
                par += nodes.strong(text=message)
            else:
                par += nodes.inline(text=message)

            if not self.options.get('hide_author'):
                par += [nodes.inline(text=" by "),
                        nodes.emphasis(text=six.text_type(commit.author))]
            if not self.options.get('hide_date'):
                par += [nodes.inline(text=" at "),
                        nodes.emphasis(text=str(date_str))]
            item.append(par)
            if detailed_message and not self.options.get('hide_details'):
                detailed_message = detailed_message.strip()
                if self.options.get('detailed-message-pre', False):
                    item.append(
                        nodes.literal_block(text=detailed_message))
                else:
                    item.append(nodes.paragraph(text=detailed_message))
            list_node.append(item)
        return [list_node]


def setup(app):
    app.add_directive('git_changelog', GitChangelog)
    app.add_directive('git_commit_detail', GitCommitDetail)
