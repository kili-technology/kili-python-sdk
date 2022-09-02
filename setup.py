"""
This script permits to setup the python package.
"""

from setuptools import find_packages, setup

from kili import __version__

setup(
    # name on pypi
    name="kili",
    # code version
    version=__version__,
    # List packages
    packages=find_packages(),
    author="Kili Technology",
    author_email="contact@kili-technology.com",
    description="Python client for Kili Technology labeling tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "pandas",
        "click",
        "requests",
        "six",
        "tabulate",
        "tqdm",
        "typeguard",
        "typing_extensions",
        "pyparsing",
        "websocket-client",
    ],
    # Taking into account MANIFEST.in
    include_package_data=True,
    # Official page
    url="https://github.com/kili-technology/kili-python-sdk",
    # Some meta data:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        ("Programming Language :: Python :: " "Implementation :: CPython"),
        ("Programming Language :: Python :: " "Implementation :: PyPy"),
    ],
    entry_points={
        "console_scripts": ["kili=kili.cli:main"],
    },
)
