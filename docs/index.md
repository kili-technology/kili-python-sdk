# Getting started with the Kili Python SDK

<img src="assets/Kili_Core_Illustration_Interact.png" alt="Kili Character" align="right" style="height:400px;"/>

## What is Kili?

Kili is a platform that empowers a data-centric approach to Machine Learning through quality training data creation. It provides collaborative data **annotation tools** and APIs that enable quick iterations between reliable dataset building and model training. More info about the product [here](https://kili-technology.com/platform/label-annotate).

If you are looking for the Kili product documentation, it is located [here](https://docs.kili-technology.com/docs).

## The Kili Python SDK

Kili Python SDK has been designed to perform complex project-related tasks by using the Python programming language. Using Kili Python SDK, you can write scripts for repetitive tasks and then integrate them in one machine learning or data science workflow. For people who are familiar with Python, it may be perfect _middle ground_ between complex [GraphQL](https://docs.kili-technology.com/docs/kili-api) queries and simple, but less flexible [CLI](https://python-sdk-docs.kili-technology.com/latest/cli/) one-liners.

## Requirements

You only need Python 3.7 or higher.

## Installation

Install the Kili client with pip:

```bash
pip install kili
```

## Usage

- Create and copy a [Kili API key](https://docs.kili-technology.com/docs/creating-an-api-key)
- Add the `KILI_API_KEY` variable in your bash environment (or in the settings of your favorite IDE) by pasting the API key value that you copied earlier:

  ```bash
  export KILI_API_KEY='<you api key value here>'
  ```

- Instantiate the Kili client:

  ```python
  from kili.client import Kili
  kili = Kili()
  ```

!!! info
You can also pass the API key as an argument during `Kili` initialization:

```python
kili = Kili(api_key='<you api key value here>')
```

!!! success "Great!"
You can now begin to use the Kili Python SDK
