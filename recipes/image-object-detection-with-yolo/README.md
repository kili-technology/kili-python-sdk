# Labelled Image Data & Transfer Learning

This recipe shows you how you can leverage Kili to rapidly create your own custom image detection model.

The main ingredients we are going to use are :

- The data you have just labelled via Kili as training set
- The excellent [yolov3](https://github.com/ultralytics/yolov3) library to craft our model

## Requirements

Please make sure to do the following before starting working on this recipe.

1. Install `kili-playground` (see the [project repository](https://github.com/kili-technology/kili-playground))
2. Install [yolov3](https://github.com/ultralytics/yolov3) by following their requirements.
3. Make the same for our recipe by installing our additional requirements : `pip install -U -r requirements.txt`
4. Our `main.py` script will require you to provide your Kili credentials, endpoint and your `yolov3` repository location path as argument. You can as well provide them by setting the following environment variables (they will be used by default by the recipe) : `EMAIL`, `PASSWORD`, `PROJECT_ID`, `API_ENDPOINT`, `YOLO_PATH`.

## Preparations

Before launching your training session, upload your dataset in kili and start labelling. Note that to use this recipe, you need to define your categories by their index (starting with zero).

## Launching your training

After having labelled a few data instances, you are ready to launch a new training using transfer learning.

Please make sure to download the `yolov3` pretrained weights you would like to use (refer to this google drive [file](https://drive.google.com/open?id=1LezFG5g3BCW6iYaV89B2i64cqEUZD7e0)) and place them in `$YOLO_PATH/weights/` (please refer to this [documentation](https://github.com/ultralytics/yolov3/wiki/Example:-Transfer-Learning)).

Next launch the following command:

```
python main.py --weights /path/to/your/weights
```

## Retraining from scratch

Note that you can also train from scratch by explicitly setting `--no_transfer`. The learning will initialize a new network starting with the specified weights as initialization.

## Hyperparameters

The following class does not expose the model hyperparameters but you can change them directly in the `$YOLO_PATH/train.py`script.
