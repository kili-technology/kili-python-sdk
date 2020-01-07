# Weak supervision with Snorkel

You may not have the capability to always label from a to z your dataset and may want to rely on semi-automated strategies to avoid the manual workload.

One strategy is to rely on weak supervision, and particularly on the features offered by [Snorkel](https://www.snorkel.org). Snorkel gives you the ability to write "labeling functions" which will encode manual rules, heuristics or a prior knowledge and predict your asset label automatically.

Once your training dataset has been labelled via labeling functions (lfs) you may directly learn a machine learning model out of these new annotations, or even review the predictions and correct eventually a few errors. It is always easier to review an annotation than doing the labelisation by yourself.

To see how you can apply Snorkel to your use case, please visit the following tutorials:

* https://www.snorkel.org/use-cases/01-spam-tutorial
* https://github.com/snorkel-team/snorkel-tutorials/tree/master/visual_relation

The script attached to this directory will guide you in uploading the predictions in Kili so that you can easily and quickly validate the Snorkel model inference results.

## Saving your predictions

Once you have run your predictor, export your predictions following the format exposed in the following `yaml` [file](../conf/new_predictions.yml).

Depending on your machine learning task, you will need to encode your prediction into a serialized json that will be sent to the API:

* Classification: we ask you to provide the categories for your asset. In case of multi-classes, an array can be provided.

```
{
    "categories":[
        {"name":"CLASS_A","confidence":100},{"name":"CLASS_B","confidence":100}
    ]
}
```

* Image / Character Recognition : provide the transcription and the bounding box information

```
{
    "annotations":[
        {
            "type":"OCR", 
            "annotation": {
                "score":null,
                "description":[{"FIRSTNAME":100}],
                "boundingPoly":[
                    {"normalizedVertices":[{"x":0.35780955025552263,"y":0.44947931541738095},{"x":0.35780955025552263,"y":0.40036713776137756},{"x":0.47033454698121024,"y":0.40036713776137756},{"x":0.47033454698121024,"y":0.44947931541738095}]}
                ],
                "type":"RECTANGLE",
                "text":"Willeke"
            }
        },
        {
            "type":"OCR",
            ...
        }
    ]
}
```


* NER: Provide the entities and their location.

```
{
    "entities":[
        {
            "groups":[],
            "name":"dolor",
            "salience":1,
            "type":"INTERJECTION",
            "mentions":[
                {"id":"1168280c-6731-453c-9ec6-45daeb609c01","type":"INTERJECTION","text":{"beginOffset":12,"content":"dolor"}}
            ]
        },
        {
            "groups":[],
            ...
        }
    ]
}
```

## Uploading your predictions

You can then use [main](./main.py) file attached to read your predictions file and upload them to Kili.