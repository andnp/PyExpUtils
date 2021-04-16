from setuptools import setup, find_packages

setup(
    name='PyExpUtils',
    url='https://github.com/andnp/PyExpUtils.git',
    author='Andy Patterson',
    author_email='andnpatterson@gmail.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'numba>=0.52.0',
        'h5py>=3.1.0',
        'filelock>=3.0.0',
    ],
    version=2.16,
    license='MIT',
    description='A small set of utilities for RL and ML experiments',
    long_description='todo',
)
