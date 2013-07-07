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
    }

    def run(self):
        env = self.state.document.settings.env
        repo = Repo(env.srcdir)
        commits = repo.iter_commits()
        l = nodes.bullet_list()
        revisions_to_display = self.options.get('revisions', 10)
        for commit in list(commits)[:revisions_to_display]:
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
