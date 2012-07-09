from datetime import datetime

from docutils import nodes
from git import Repo
from sphinx.util.compat import Directive


class GitChangelog(Directive):

    def run(self):
        env = self.state.document.settings.env
        repo = Repo(env.srcdir)
        commits = repo.iter_commits()
        l = nodes.bullet_list()
        for commit in list(commits)[:10]:
            date_str = datetime.fromtimestamp(commit.authored_date)
            item = nodes.list_item()
            item += [
                nodes.strong(text=commit.message),
                nodes.inline(text=" by "),
                nodes.emphasis(text=str(commit.author)),
                nodes.inline(text=" at "),
                nodes.emphasis(text=str(date_str))
            ]
            l.append(item)
        return [l]



def setup(app):
    app.add_directive('git_changelog', GitChangelog)
