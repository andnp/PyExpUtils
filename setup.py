from setuptools import setup, find_packages

setup(
    name='PyExpUtils',
    url='https://github.com/andnp/PyExpUtils.git',
    author='Andy Patterson',
    author_email='andnpatterson@gmail.com',
    packages=[ p for p in find_packages() if 'tests' not in p ],
    install_requires=[],
    version='0.0',
    license='MIT',
    description='A small set of utilities for RL and ML experiments',
    long_description='todo',
)
