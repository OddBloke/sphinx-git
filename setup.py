from setuptools import setup


setup(
    name='sphinx-git',
    description='git Changelog for Sphinx',
    version='6',
    author='Daniel Watkins',
    author_email='daniel@daniel-watkins.co.uk',
    install_requires=['sphinx', 'GitPython'],
    url="https://github.com/OddBloke/sphinx-git",
    py_modules=['sphinx_git'],
)
