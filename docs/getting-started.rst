Getting Started
===============

Including sphinx-git In Your Project
------------------------------------

This guide assumes that you already have a Sphinx documentation project
configured and building.  If that is not the case, see `the Sphinx
documentation`_ first and then come back.

Installing sphinx-git
~~~~~~~~~~~~~~~~~~~~~

The first thing you will need to do is install sphinx-git::

    pip install sphinx-git

You may also want to include it in your setup.py or requirements.txt to ensure
that sphinx-git is installed wherever you generate your documentation; each
project will probably have a different way of doing this.

Including sphinx-git In Your Sphinx Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have installed sphinx-git, you need to configure Sphinx to look for
it.  Find the Sphinx conf.py which is used to generate your documentation.
Somewhere in that file (generally towards the top), you will find the
``extensions`` setting.  Add ``sphinx_git`` to this list (note the
underscore)::

    extensions = ['sphinx_git']

Add A git Changelog To Your Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the hard parts are done, now you can add a git changelog to your project!
Find a documentation file where you want it and add::

    Recent Changes
    --------------

    .. git_changelog::

Build your documentation and, voila!, you have a git changelog right there in
your docs!

There are a number of ways you can configure sphinx-git to output precisely
what you want, which are outlined in the next section of the documentation.


.. _the Sphinx documentation: http://sphinx-doc.org/tutorial.html

Add Details of the Latest Commit to Your Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also display information about the state of the repository when the documentation
was compiled with the ``git_commit_detail`` directive::

    .. git_commit_detail::
        :branch:
        :commit: