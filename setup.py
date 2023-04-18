"""This script permits to setup the python package."""

from setuptools import find_packages, setup

from src.kili import __version__

install_requires = [
    "pandas>=1.0.0,<2.0.0",
    "click>=8.0.0, <9.0.0",
    "requests>=2.0.0, <3.0.0",
    "tabulate>=0.9.0,<0.10.0",
    "tenacity>=8.0.0, <9.0.0",
    "tqdm>=4.0.0, <5.0.0",
    "typeguard>=2.0.0,<3.0.0",
    "typing_extensions>=4.1.0,<5.0.0",
    "pyparsing>=3.0.0,<4.0.0",
    "websocket-client>=1.0.0,<2.0.0",
    "pyyaml>=6.0,<7.0",
    "Pillow>=9.0.0,<10.0.0",
    "cuid>=0.4,<0.5",
    "pydantic>=1.0.0,<2.0.0",
    "urllib3>=1.26,<2.0",
    "ffmpeg-python>=0.2.0,<0.3.0",
    "gql[requests,websockets]>=3.0.0,<4.0.0",
]

image_requires = [
    "opencv-python>=4.0.0,<5.0.0",
]

dev_extra = [
    # release
    "bump2version>=1.0.0",
    # tests
    "pytest>=7.0.0",
    "pytest-mock>=3.0.0",
    "pytest-cov>=4.0.0",
    "pytest-xdist[psutil]>=3.0.0",
    # documentation
    "mkdocs>=1.0.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings>=0.20.0, <0.21.0",
    "mkdocstrings-python-legacy>=0.2.0,<0.3.0",
    "mkdocs-click>=0.8.0,<0.9.0",
    "mike>=1.0.0",
    "pymdown-extensions>=9.0",
    # linting
    "black>=23.0.0",
    "pre-commit>=3.0.0",
    "pylint>=2.0.0",
    "flake8-unused-arguments>=0.0.13,<0.0.14",
    "pyright>=1.0.0",
    # notebooks tests
    "nbformat>=5.0.0",
    "nbconvert>=7.0.0",
    "ipykernel>=6.0.0",
    # image utils
    "opencv-python>=4.0.0",
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
    extras_require={
        "dev": dev_extra,
        "image-utils": image_requires,
    },
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
