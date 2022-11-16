# Kili Python SDK

<img src="assets/Kili_Core_Illustration_Interact.png" alt="Kili Character" align="right" style="height:400px;"/>
## What is Kili?
Kili is a platform that empowers a data-centric approach to Machine Learning through quality training data creation. It provides collaborative data **annotation tools** and APIs that enable quick iterations between reliable dataset building and model training. More info about the product [here](https://kili-technology.com/product/label-annotate).

If you are looking for the Kili product documentation, it is located [here](https://docs.kili-technology.com/docs).

## Requirements

You only need Python 3.7 or greater

## Installation

Install the Kili client with pip:

```bash
pip install kili
```

## Getting Started

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

!!! success "Great!"
    You can now begin to use the Kili Python SDK

!!! info
    You can also pass the API key as an argument of the `Kili` initialization:
    `python kili = Kili(api_key='<you api key value here>') `
