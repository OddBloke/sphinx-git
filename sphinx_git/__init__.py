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

from datetime import datetime

import six
from docutils import nodes
from docutils.parsers.rst import directives
from git import Repo
from sphinx.util.compat import Directive


# pylint: disable=too-few-public-methods, abstract-method
class GitDirectiveBase(Directive):
    def _find_repo(self):
        env = self.state.document.settings.env
        repo = Repo(env.srcdir, search_parent_directories=True)
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
        self.branch_name = self.repo.head.ref.name
        self.commit = self._get_commit()
        self.sha_length = self.options.get('sha_length',
                                           self.default_sha_length)
        markup = self._build_markup()
        return markup

    def _get_commit(self):
        repo = self._find_repo()
        return repo.commit()

    def _build_markup(self):
        field_list = nodes.field_list()
        item = nodes.paragraph()
        item.append(field_list)
        if 'branch' in self.options:
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
            else:
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
            return repo.iter_commits(rev=self.options['rev-list'])
        commits = repo.iter_commits()
        revisions_to_display = self.options.get('revisions', 10)
        return list(commits)[:revisions_to_display]

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
            item += [
                nodes.strong(text=message),
                nodes.inline(text=" by "),
                nodes.emphasis(text=six.text_type(commit.author)),
                nodes.inline(text=" at "),
                nodes.emphasis(text=str(date_str))
            ]
            if detailed_message:
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
