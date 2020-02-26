FROM ultralytics/yolov3:v98

RUN pip install -U kili

WORKDIR /app
ADD . /app

ENV EMAIL=$EMAIL
ENV PASSWORD=$PASSWORD
ENV PROJECT_ID=$PROJECT_ID
ENV API_ENDPOINT=$API_ENDPOINT
ENV JOB_ID=$JOB_ID
ENV PYTHONPATH=/usr/src/app

RUN /app/yolov3/weights/download_yolov3_weights.sh

ENTRYPOINT [ "python", "/app/main.py" ]
