# Recipes

## How to create a project

You can refer to the following [documentation](https://kili-technology.github.io/kili-docs/docs/python-graphql-api/create-a-project).

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

## How to do online learning with AutoML (Text Classification Single-class)

- Create Project for TextClassification Single-class

- Then execute:

```bash
python online_learning_text_classification.py (OPTIONAL --api_endpoint https://cloud.kili-technology.com/api/label/graphql)
```

- Enter your personnal information : Mail, Password, ProjectID

- Annotate

- See predictions

### In docker

1. Create a `.env` file in this folder containing your settings:

```bash
EMAIL=
PASSWORD=
PROJECT_ID=
API_ENDPOINT=
```

2. Build the docker and launch it:

```bash
docker build -t kili-playground .

docker run -it --network="host" kili-playground online-learning
```

## How to do online learning with YOLOv3 (for object detection)

1. Create a project for single-class object detection

2. Update settings to respect YOLOv3's way of dealing with classes
   (key is an integer starting from zero and value is in lower case)

```
{
  "filetype": "IMAGE",
  "jobs": {
    "OBJECT_DETECTION": {
      "mlTask": "OBJECT_DETECTION",
      "content": {
        "input": "radio",
        "categories": {
          "0": {
            "name": "face"
          },
          ...
        }
      },
      "required": true,
      "tools": [
        "polygon"
      ],
      "instruction": "Detect following objects"
    }
  }
}
```

You can use Kili Playground's recipe `update_interface_settings` to programmatically update interface.

3. Build the docker in the folder:

```bash
cd image-object-detection-with-yolo
docker build -t kili-playground-yolo .
```

4. Launch it by setting `EMAIL`/`PASSWORD`/`PROJECT_ID`/`API_ENDPOINT`
   environment variables:

```bash
docker run -it -e "EMAIL=myemail@kili-technology.com" \
  -e "PASSWORD=my_password" \
  -e "PROJECT_ID=1234567890" \
  -e "JOB_ID=job_12345" \
  -e "API_ENDPOINT=https://cloud.kili-technology.com/api/label/graphql" \
  --network="host" kili-playground-yolo
```

You can also launch the script manually:

```
git clone git@github.com:ultralytics/yolov3.git /path/to/yolov3
python main.py --weights /path/to/weights/yolov3.pt \
  --email=myemail@kili-technology.com \
  --password=mypassword \
  --project_id=1234567890 \
  --job_id=job_12345 \
  --api_endpoint=https://cloud.kili-technology.com/api/label/graphql \
  --yolo_path=/path/to/yolov3
```

5. The script will continuously create predictions on non-labelled assets.

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

Use:

```bash
from kili.authentication import KiliAuth
from kili.playground import Playground

kauth = KiliAuth(email=email, password=password)
playground = Playground(kauth)
```

## How to delete one asset identified by its external id ?

Use:

```bash
playground.delete_assets_by_external_id(project_id=project_id, external_id=external_id)
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
