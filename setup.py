from setuptools import setup


execfile('sphinx_git/version.py')


setup(
    name='sphinx-git',
    description='git Changelog for Sphinx',
    version=__version__,
    author='Daniel Watkins',
    author_email='daniel@daniel-watkins.co.uk',
    install_requires=['sphinx', 'GitPython>=0.3.6'],
    url="https://github.com/OddBloke/sphinx-git",
    packages=['sphinx_git'],
)
