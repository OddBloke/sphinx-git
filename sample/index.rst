Welcome to sphinx-git Example's documentation!
==============================================

Example ``git_changelog`` Output
--------------------------------

Default
~~~~~~~

.. git_changelog::


Only 5 Revisions
~~~~~~~~~~~~~~~~

.. git_changelog::
  :revisions: 5

Range of Revisions (v2 to v4)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. git_changelog::
  :rev-list: v2..v4

Both Options
~~~~~~~~~~~~

This will generate a warning.

.. git_changelog::
  :rev-list: v2..v4
  :revisions: 2
