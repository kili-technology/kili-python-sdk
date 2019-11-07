# Tutorials

## How to create a project

Update `new_project.yml` with your values.

Then execute:

```bash
python create_project.py --configuration_file ./new_project.yml --graphql_client https://cloud.kili-technology.com/api/label/graphql
```

## How to pre-annotate assets

### Named-entity recognition

Create a NER project and retrieve its ID.

Make sure that your GCP authentication is set up properly (or follow [this tutorial](https://cloud.google.com/natural-language/docs/reference/libraries)).

Then execute:

```bash
python ner/insert_google_predictions.py
```

## How to massively add users

Edit `new_users.yml`.

Execute:

```bash
python add_users.py
```

**Note:** You need to have ADMIN right at Organization level to create users.

## How to export and parse labels

Execute:

```bash
python export_labels.py
```
