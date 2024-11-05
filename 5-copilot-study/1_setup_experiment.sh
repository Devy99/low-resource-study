#!/bin/bash

# Create 50 directories named copilot_study_1, copilot_study_2, ..., copilot_study_50
for i in {1..50}; do
DIR_NAME="copilot_study_$i"
  mkdir -p $DIR_NAME
  echo "Created directory $DIR_NAME"

  cp prepare_datasets.py $DIR_NAME
  cp -r prompts_prefix $DIR_NAME
  cd $DIR_NAME
  python3 -u prepare_datasets.py
  cd ..
done