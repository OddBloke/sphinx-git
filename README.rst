sphinx-git
----------

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

Example
=======

You can see a live example `in the Read the Docs documentation`_; the HTML output looks like this:

.. image:: https://user-images.githubusercontent.com/62736/34072980-a8469baa-e25e-11e7-968f-553caad65e56.png

.. _Sphinx documentation tool: http://sphinx-doc.org/
.. _the documentation on Read the Docs: http://sphinx-git.readthedocs.org/en/latest/?utm_source=github&utm_medium=github&utm_campaign=github
.. _in the Read the Docs documentation: http://sphinx-git.readthedocs.io/en/stable/using.html#git-changelog-directive
