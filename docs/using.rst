Using sphinx-git
================

Currently, sphinx-git provides a single extension to Sphinx: the
``git_changelog`` directive.

git_changelog Directive
-----------------------

The ``git_changelog`` directive produces a list of commits in the repository in
which the documentation build is happening.

By default, it will output the most recent 10 commits.  So::

    .. git_changelog::

produces:

    .. git_changelog::

As you can see, each revision has the message, author and date output in a
list.  If a commit has a detailed message (i.e. any part of the commit message
that is not on the first line), that will be output below the list item for
that commit.

Changing Number of Revisions in Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to change the number of revisions output by ``git_changelog``, then
you can specify the ``:revisions:`` argument.  So::

    .. git_changelog::
        :revisions: 2

produces:

    .. git_changelog::
        :revisions: 2

If you specify more revisions than the history contains, all revisions in the
history will be displayed.

Specifying Range of Revisions to Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want even more control over the output of ``git_changelog``, then you
can specify precisely the revisions you want included using the ``:rev-list:``
argument.  So::

    .. git_changelog::
        :rev-list: v3..v4

produces a list of all the commits between the v3 and v4 tags:

    .. git_changelog::
        :rev-list: v3..v4

and::

    .. git_changelog::
        :rev-list: v1

gives you a list of all commits up to the v1 tag (most of which involved me
wrestling with setuptools):

    .. git_changelog::
        :rev-list: v1

``:rev-list:`` lets you specify revisions using anything that ``git rev-parse``
will accept.  See `the man page`_ for details.

.. warning::

    The ``:revisions:`` argument and the ``:rev-list:`` argument don't play
    nicely together.  ``:rev-list:`` will always take precedence, and all
    commits specified by the revision specification be output regardless of the
    ``:revisions:`` argument [#patches]_.

    Sphinx will output a warning if you specify both.

Preformatted Output for Detailed Messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would prefer for the detailed commit messages to be output as
preformatted text (e.g. if you include code samples in your commit messages),
then you can specify this preference using the ``:detailed-message-pre:``
argument. So::

    .. git_changelog::
        :rev-list: 3669419^..3669419
        :detailed-message-pre: True

becomes:

    .. git_changelog::
        :rev-list: 3669419^..3669419
        :detailed-message-pre: True

.. _the man page: https://www.kernel.org/pub/software/scm/git/docs/git-rev-parse.html

.. rubric:: Footnotes

.. [#patches]
    :doc:`Patches welcome! <contributing>`
