Enabling on Read the Docs
=========================

`Read the Docs`_ is an excellent website that hosts Sphinx-generated
documentation (including `the documentation for this project`_, which is
probably where you are reading it).  This document assumes that you already
have your project configured on Read the Docs, using their default
configuration [#read-the-docs-getting-started]_.

As a custom extension, sphinx-git isn't supported out-of-the-box by Read the
Docs, but it is very easy to get it working!

Creating a Documentation Requirements File
------------------------------------------

The first thing you'll need to do is create a `pip requirements file`_
for your documentation.  Create a file containing::

    sphinx-git

and commit it somewhere in your repository [#pinning]_ (I will assume it is in
``requirements/doc.txt`` for the rest of this document).

Configuring Read the Docs
-------------------------

Navigate to the Read the Docs admin page for your project.  This will be of the
form ``https://readthedocs.org/dashboard/<PROJECT NAME>/edit/``.  Once on this
page, you need to do two things:

* Tick the box under "Use virtualenv", so that Read the Docs will install our
  custom documentation requirements, and
* Enter your documentation requirements file name in the "Requirements file"
  box (``requirements/doc.txt`` from above).

Submitting the form should cause your project to be rebuilt, now with
sphinx-git available!

.. _Read the Docs: https://readthedocs.org/
.. _the documentation for this project: http://sphinx-git.readthedocs.org/en/latest/
.. _pip requirements file: http://www.pip-installer.org/en/latest/cookbook.html#requirements-files

.. rubric:: Footnotes

.. [#read-the-docs-getting-started]
    Follow `the Read the Docs getting started guide
    <https://read-the-docs.readthedocs.org/en/latest/getting_started.html>`_ if
    you haven't already.

.. [#pinning]
    You should probably pin that requirement to a specific version, but that is
    outside the scope of this documentation. This is probably a good place to
    start reading about it: http://nvie.com/posts/pin-your-packages/
