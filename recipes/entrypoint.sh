#!/bin/bash

set -xe

if [[ "$1" == 'online-learning' ]]; then
  echo "Entrypoint $1"
  source .env
  python3 online_learning_text_classification.py
fi
