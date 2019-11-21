# Recipes

## How to create a project

1. Update `new_project.yml` with your values.

2. Execute:

```bash
python create_project.py --configuration_file ./conf/new_project.yml --graphql_client https://cloud.kili-technology.com/api/label/graphql
```

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

## How to import assets with metadata

1. Edit `new_assets.yml`. Metadata may contain some information about assets. Used for interface category `IMAGE_WITH_SEARCH`.

2. Execute:

```bash
python import_assets.py
```

To massively import data:

```bash
python import_assets_by_chunks.py
```

## How to import assets with S3

1. Edit `new_assets_with_s3.yml`.

2. Execute:

```bash
python import_assets_with_s3.py
```

## How to delete all assets

1. Execute:

```bash
python delete_all_assets.py
```

## How to push pre-annotation to existing assets

1. Edit `new_predictions.yml`.

2. Execute:

```bash
python import_predictions.py
```

## How to export and parse labels

1. Execute:

```bash
python export_labels.py
```

## How to do Named-Entity Recognition with Google

Example based on Enron email dataset. Its downloads the data, get the first 50 emails, pre-label them with Google NLP, push both assets and predictions to Kili and prioritize the assets.

1. Create a NER project and retrieve its ID.

2. Make sure that your GCP authentication is set up properly (or follow [this tutorial](https://cloud.google.com/natural-language/docs/reference/libraries)).

3. Execute:

```bash
python google_ner_pre_labeling.py
```

## How to use GraphQL Playground

For more flexibility, you can directly query GraphQL API without using
`kili-playground`.

1. Go to http://cloud.kili-technology.com/api/label/playground

2. Login using the following mutation in order to retrieve the authentication token:

```graphql
mutation {
  signIn(email: "YOUR_EMAIL", password: "YOUR_PASSWORD") {
    user {
      id
    }
    token
  }
}
```

3. In the bottom left corner of the screen, click on `HTTP headers` and write
   the retrieved token in the authorization headers:

```json
{
  "Authorization": "Bearer: YOUR_TOKEN"
}
```

4. Launch any query/mutation:

```graphql
query {
  getUser(email: "YOUR_EMAIL") {
    id
  }
}
```

## How to append assets and leverage online learning with AutoML

- Create Project for TextClassification with `JsonSetting = "{\"categories\":{\"POSITIVE\": \"Review positive\",\"NEGATIVE\": \"Review négative\"}}"`

- Then execute:

```bash
python python create_auto_model.py (OPTIONNAL --api_endpoint https://cloud.kili-technology.com/api/label/graphql)
```

- Enter your personnal information : Mail, Password, ProjectID

- Annotate

- See predictions

## How to import OCR metadata

1. Edit `new_assets.yml` where metadata has the format of `./examples/invoice.json` and the content points to the URL of `invoice.png`.

2. Execute:

```bash
python import_assets.py
```
