# Copyright 2012 (C) Daniel Watkins <daniel@daniel-watkins.co.uk>
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

from docutils import nodes
from docutils.parsers.rst import directives
from git import Repo
from sphinx.util.compat import Directive


class GitChangelog(Directive):

    option_spec = {
        'revisions': directives.nonnegative_int,
        'rev-list': unicode,
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

    def _find_repo(self):
        env = self.state.document.settings.env
        repo = Repo(env.srcdir)
        return repo

    def _filter_commits(self, repo):
        if 'rev-list' in self.options:
            return repo.iter_commits(rev=self.options['rev-list'])
        commits = repo.iter_commits()
        revisions_to_display = self.options.get('revisions', 10)
        return list(commits)[:revisions_to_display]

    def _build_markup(self, commits):
        l = nodes.bullet_list()
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
                nodes.emphasis(text=str(commit.author)),
                nodes.inline(text=" at "),
                nodes.emphasis(text=str(date_str))
            ]
            if detailed_message:
                item.append(nodes.caption(text=detailed_message.strip()))
            l.append(item)
        return [l]


def setup(app):
    app.add_directive('git_changelog', GitChangelog)
