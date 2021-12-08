# Recipes

## How to create a project

You can refer to the following [documentation](https://cloud.kili-technology.com/docs/python-graphql-api/create-a-project).
You can also refer to [our recipe on how to create a project](https://github.com/kili-technology/kili-playground/blob/master/recipes/create_project.ipynb) (run it [here](https://colab.research.google.com/github/kili-technology/kili-playground/blob/master/recipes/create_project.ipynb))

## How to update interface settings

1. Edit `new_interface_settings.json`.

2. Execute:

```bash
python update_interface_settings.py
```

## How to massively add users

1. Edit `new_users.yml`.

2. Execute:

```bash
python add_users.py
```

**Note:** You need to have ADMIN right at Organization level to create users.

## How to import assets

Check out [our recipe on how to import assets](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_assets.ipynb) (run it [here](https://colab.research.google.com/github/kili-technology/kili-playground/blob/master/recipes/import_assets.ipynb))

## How to delete all assets

1. Execute:

```bash
python delete_all_assets.py
```

## How to push pre-annotation to existing assets

Check out [our recipe on how to import predictions](https://github.com/kili-technology/kili-playground/blob/master/recipes/import_predictions.ipynb) (run it [here](https://colab.research.google.com/github/kili-technology/kili-playground/blob/master/recipes/import_predictions.ipynb))

## How to export and parse labels

Check out [our recipe on how to export labels](https://github.com/kili-technology/kili-playground/blob/master/recipes/export_labels.ipynb) (run it [here](https://colab.research.google.com/github/kili-technology/kili-playground/blob/master/recipes/export_labels.ipynb))

## How to do Named-Entity Recognition with Google

Example based on Enron email dataset. Its downloads the data, get the first 50 emails, pre-label them with Google NLP, push both assets and predictions to Kili and prioritize the assets.

1. Create a NER project and retrieve its ID.

2. Make sure that your GCP authentication is set up properly (or follow [this tutorial](https://cloud.google.com/natural-language/docs/reference/libraries)).

3. Execute:

```bash
python google_ner_pre_labeling.py
```

## How to use Python functions to query data

You can query every asset, label, or project-related information through the API.
A comprehensive example is [our recipe on how to use the query methods](https://github.com/kili-technology/kili-playground/blob/master/recipes/query_methods.ipynb) (run it [here](https://colab.research.google.com/github/kili-technology/kili-playground/blob/master/recipes/query_methods.ipynb))
You can also refer to the [documentation](https://cloud.kili-technology.com/docs/python-graphql-api/playground-api/).

## How to use GraphQL Playground to query data

If you prefer, you can directly query GraphQL API without using
`kili-playground`.

1. Generate an API key in Kili interface in [My account](https://cloud.kili-technology.com/label/my-account), under the tab API KEY. Store it in some place secured.

2. Go to http://cloud.kili-technology.com/api/label/v2/graphql

3. In the bottom left corner of the screen, click on `HTTP headers` and write
   the retrieved token in the authorization headers:

```json
{
  "Authorization": "X-API-Key: YOUR_API_KEY"
}
```

4. Launch any query/mutation:

```graphql
query {
  users(where: { email: "YOUR_EMAIL" }, first: 10, skip: 0) {
    id
    activated
    email
  }
}
```

## How to import OCR metadata

1. Edit `new_assets.yml` where metadata has the format of `./examples/invoice.json` and the content points to the URL of `invoice.png`.

2. Execute:

```bash
python import_assets.py
```

## How to set assets only to be labeled by some users

1. Edit `new_assets.yml` and change the field `toBeLabeledBy`. When this field no exists, assets can be labeled by everyone.

2. Execute:

```bash
python set_asset_to_be_labeled_by.py
```

## How to authenticate to the API ?

1. Generate an API key in Kili interface in [My account](https://cloud.kili-technology.com/label/my-account), under the tab API KEY. Store it in some place secured.

2. Start automating your tasks :

```bash
from kili.client import Kili

kili = Kili(api_key=api_key)
```

## How to delete one asset identified by its external id ?

Use:

```bash
assets = kili.assets(project_id=project_id, external_id_contains=[external_id])
kili.delete_many_from_dataset(asset_ids=[a['id] for a in assets])
```

## How to update instructions in project?

Currently instructions can be set as a link to a PDF or an external web page.

You can update instructions with:

```bash
python update_project_instructions.py
```

## How to get labeler statistics?

You can get an excel file summing up the asset / labeler / day doing:

```bash
python get_labeler_stats.py
```
