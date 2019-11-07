# Tutorials

## How to create a project

Update `new_project.yml` with your values.

Then execute:

```bash
python create_project.py --configuration_file ./new_project.yml --graphql_client https://cloud.kili-technology.com/api/label/graphql
```

## How to append assets and predictions with AutoML

- Create Project for TextClassification with `JsonSetting = "{\"categories\":{\"POSITIVE\": \"Review positive\",\"NEGATIVE\": \"Review négative\"}}" `
 
- Download IMDB dataset on `https://www.kaggle.com/iarunava/imdb-movie-reviews-dataset`

- Then execute:
```bash
python python create_auto_model.py --mail MY_MAIL --graphql_client https://cloud.kili-technology.com/api/label/graphql --data_path PATH_TO_IMDB --figure_path PATH_TO_FIGURES
```
- Enter your project ID

- Annotate