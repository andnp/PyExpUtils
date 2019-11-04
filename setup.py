from setuptools import setup, find_packages

setup(
    name='PyExpUtils',
    url='https://github.com/andnp/PyExpUtils.git',
    author='Andy Patterson',
    author_email='andnpatterson@gmail.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=[],
    version=0.17,
    license='MIT',
    description='A small set of utilities for RL and ML experiments',
    long_description='todo',
)
