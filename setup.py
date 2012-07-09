from setuptools import find_packages,setup


setup(
    name='sphinx-git',
    description='git Changelog for Sphinx',
    version='1',
    author='Daniel Watkins',
    author_email='daniel@daniel-watkins.co.uk',
    packages=find_packages(),
    install_requires=['sphinx', 'GitPython'],
    url="https://github.com/OddBloke/sphinx-git",
)
