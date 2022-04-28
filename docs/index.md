# Kili Python SDK

<img src="assets/Kili_Core_Illustration_Interact.png" alt="Kili Character" align="right" style="height:400px;"/>
## What is Kili?
Kili is a platform that empowers a data-centric approach to Machine Learning through quality training data creation. It provides collaborative data **annotation tools** and APIs that enable quick iterations between reliable dataset building and model training. More info [here](https://kili-technology.com/product/label-annotate).

## Requirements

- `python >= 3.7`
- Create and copy a Kili API key
- Add the `KILI_API_KEY` variable in your bash environment (or in the settings of your favorite IDE) by pasting the API key value you copied above:

```bash
export KILI_API_KEY='<you api key value here>'
```

## Installation

Install the Kili client with pip:

```bash
pip install kili
```

## Usage

Instantiate the Kili client:

```python
from kili.client import Kili
kili = Kili()
# You can now use the Kili client!
```

Note that you can also pass the API key as an argument of the `Kili` initialization:

```python
kili = Kili(api_key='MY API KEY')
```
