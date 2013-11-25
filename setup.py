from setuptools import setup


setup(
    name='sphinx-git',
    description='git Changelog for Sphinx',
    version='7',
    author='Daniel Watkins',
    author_email='daniel@daniel-watkins.co.uk',
    install_requires=['sphinx', 'GitPython>=0.3.2.RC1'],
    url="https://github.com/OddBloke/sphinx-git",
    py_modules=['sphinx_git'],
)
