"""
This script permits to setup the python package.
"""

from setuptools import find_packages, setup

from src.kili import __version__

install_requires = [
    "pandas",
    "click",
    "requests",
    "tabulate",
    "tenacity",
    "tqdm",
    "typeguard<3.0.0",
    "typing_extensions>=4.1.0",
    "pyparsing",
    "websocket-client",
    "pyyaml",
    "Pillow",
    "cuid",
    "pydantic<2",
    "urllib3>=1.26,<2.0.0",
    "ffmpeg-python",
    "gql[requests,websockets]",
    "pip-system-certs>=4.0.0,<5.0.0",
]

dev_extra = [
    # release
    "bump2version",
    # tests
    "pytest",
    "pytest-mock",
    "pytest-cov",
    "pytest-xdist[psutil]",
    "pytest-timeout",
    # documentation
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings",
    "mkdocstrings-python-legacy",
    "mkdocs-click",
    "mike",
    "pymdown-extensions",
    # linting
    "black==23.1.0",
    "pre-commit",
    "pylint==2.17.1",
    "flake8-unused-arguments",
    "pyright==1.1.300",
    # notebooks tests
    "nbformat",
    "nbconvert",
    "ipykernel",
]

setup(
    name="kili",
    version=__version__,
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests"]),
    author="Kili Technology",
    author_email="contact@kili-technology.com",
    description="Python client for Kili Technology labeling tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    extras_require={"dev": dev_extra},
    include_package_data=True,
    entry_points={
        "console_scripts": ["kili=kili.cli:main"],
    },
    url="https://github.com/kili-technology/kili-python-sdk",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
