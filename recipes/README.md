# Tutorials

## How to create a project

1. Update `new_project.yml` with your values.

2. Execute:

```bash
python create_project.py --configuration_file ./new_project.yml --graphql_client https://cloud.kili-technology.com/api/label/graphql
```

## How to pre-annotate assets

### Named-entity recognition

1. Create a NER project and retrieve its ID.

2. Make sure that your GCP authentication is set up properly (or follow [this tutorial](https://cloud.google.com/natural-language/docs/reference/libraries)).

3. Execute:

```bash
python ner/insert_google_predictions.py
```

### Image object detection

## How to massively add users

1. Edit `new_users.yml`.

2. Execute:

```bash
python add_users.py
```

**Note:** You need to have ADMIN right at Organization level to create users.

## How to export and parse labels

1. Execute:

```bash
python export_labels.py
```
