from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='PyExpUtils-andnp',
    url='https://github.com/andnp/PyExpUtils.git',
    author='Andy Patterson',
    author_email='andnpatterson@gmail.com',
    packages=find_packages(exclude=['tests*']),
    version='3.0.0',
    license='MIT',
    description='A small set of utilities for RL and ML experiments',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=[
        'numba>=0.52.0',
        'h5py>=3.1.0',
        'filelock>=3.0.0',
    ],
)
