.. image:: https://travis-ci.org/OddBloke/sphinx-git.png?branch=master
    :target: https://travis-ci.org/OddBloke/sphinx-git

sphinx-git is an extension to the `Sphinx documentation tool`_ that allows you
to include excerpts from your git history within your documentation.  This
could be used for release changelogs, to pick out specific examples of history
in documentation, or just to surface what is happening in the project.

To use it, add 'sphinx_git' to 'extensions' in your Sphinx conf.py, and add::

    .. git_changelog::

where you want the list of commits to appear.

For more details, see `the documentation on Read the Docs`_.

.. _Sphinx documentation tool: http://sphinx-doc.org/
.. _the documentation on Read the Docs: http://sphinx-git.readthedocs.org/en/latest/?utm_source=github&utm_medium=github&utm_campaign=github
