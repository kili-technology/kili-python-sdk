# Image and Text Annotation Tool - Kili Playground

## What is Kili Technology?

Kili Technology is an image, text and voice data annotation tool designed to help companies deploy machine learning applications faster. In a few minutes you can start annotating your data thanks to a catalogue of intuitive and configurable interfaces. You can easily accelerate the labeling process by connecting one of your models to pre annotate the data. The work of the annotators is 2 to 5 times faster. Kili Technology facilitates collaboration between technical teams and the business, but also with outsourced annotation companies. Data governance is managed, and production quality control is facilitated. Kili Technology meets the needs of small teams as well as those of large companies with massive stakes.

Kili Technology allows you to:

- Quickly annotate **text**, **images**, **video**, **audio** thanks to simple and intuitive interfaces
- Easily ingest data, in drag & drop, from your cloud provider, or while keeping your data On Premise, when necessary.
- Manage participants, roles and responsibilities
- Monitor production quality using leading indicators and workflows for production monitoring and data quality validation
- Easily export the produced data

### Text annotation example

![](https://github.com/kili-technology/kili-docs/blob/gh-pages/img/AM_10s.gif)

### Image annotation example

![](https://github.com/kili-technology/kili-docs/blob/gh-pages/img/VDX_10s.gif)

## What is Kili Playground ?

Kili Playground is a Python client wrapping the GraphQL API of Kili Technology.
It allows data scientists and developers to control Kili Technology from an IDE.

## Installation

- Clone the repository and install with pip

```bash
pip install kili
```

- **Note**: If you're on Windows, install Shapely by following [this tutorial](https://towardsdatascience.com/install-shapely-on-windows-72b6581bb46c).

## Get started

```python
from kili.authentication import KiliAuth
from kili.playground import Playground
kauth = KiliAuth(email, password)
playground = Playground(kauth)
```

Here are [some recipes](/recipes/). Among them:

- How to create a project
- How to pre-annotate assets
- How to massively add users
- How to export and parse labels

If you want more details on what you can do with the API, follow the [technical documentation](https://kili-technology.github.io/kili-docs/docs/graphql-api/api-graphql).
