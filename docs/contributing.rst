Contributing
============

sphinx-git is already the work of more than just myself! There are a number of
ways that you can contribute to the sphinx-git project.

Open Issues on GitHub
---------------------

If there's a problem with how sphinx-git works, or if there's a feature that
you'd like to see, `open up an issue in GitHub`_.  Give as much information as
you can and I'll do my best to get to it!


Submit a Patch
--------------

If you feel confident enough, have a stab at scratching your own itch in
sphinx-git.  Fork the project on GitHub, make your changes and submit a pull
request.

Pull requests will need to pass the `Travis CI build`_, which uses tox.
You can run this by doing the following::

    $ pip install tox
    $ tox

This will run the build on all supported Python versions.  If you're on
an environment that doesn't have both available then do the best you
can, and then open up your pull request; Travis will pick this up and
build it for you.

Pull Request Checklist
~~~~~~~~~~~~~~~~~~~~~~

Once you've got a patch ready, check the following things:

* You've written tests for your change
* The Travis CI build passes; this includes:

  * PEP-8 on the sphinx_git package and the tests
  * Pylint on the sphinx_git package
  * Passing unit tests (of course!)
* You've added a line to the CHANGELOG
* You've added documentation (if appropriate)

.. _open up an issue in GitHub: https://github.com/OddBloke/sphinx-git/issues/new
.. _Travis CI build: https://travis-ci.org/OddBloke/sphinx-git/pull_requests
