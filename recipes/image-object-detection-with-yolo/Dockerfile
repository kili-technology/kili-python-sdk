FROM ultralytics/yolov3:v98

RUN pip install -U \
  kili \
  gdown

WORKDIR /app
ADD . /app

ENV EMAIL=$EMAIL
ENV PASSWORD=$PASSWORD
ENV PROJECT_ID=$PROJECT_ID
ENV API_ENDPOINT=$API_ENDPOINT
ENV PYTHONPATH=/usr/src/app

RUN /app/download_yolov3_weights.sh

ENTRYPOINT [ "python", "/app/online_learning_image_object_detection.py" ]
