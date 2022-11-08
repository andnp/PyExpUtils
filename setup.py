from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="PyExpUtils-andnp",
    url="https://github.com/andnp/PyExpUtils.git",
    author="Andy Patterson",
    author_email="andnpatterson@gmail.com",
    packages=find_packages(exclude=["tests*", "scripts*", "typings*", "mock_repo*"]),
    package_data={"PyExpUtils": ["py.typed"]},
    version="3.3.0",
    license="MIT",
    description="A small set of utilities for RL and ML experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=[
        "numba>=0.52.0",
        "numpy>=1.21.5",
        "h5py>=3.1.0",
        "filelock>=3.0.0",
        "pandas",
    ],
    extras_require={
        "dev": [
            "mypy>=0.942",
            "flake8>=4.0.1",
            "commitizen",
            "pre-commit",
            "pipenv-setup[black]",
            "matplotlib",
            "types-filelock",
            "build",
            "twine",
            "vistir==0.6.1",
        ]
    },
)
