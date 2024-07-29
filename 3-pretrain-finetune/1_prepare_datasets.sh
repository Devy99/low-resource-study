#!/bin/bash

HF_TOKEN=$1

OUTPUT_DATASET_DIR="./datasets"
mkdir -p $OUTPUT_DATASET_DIR

echo "===================== FETCHING DATASETS ====================="
python3 -u fetch_datasets.py --token $HF_TOKEN --output-dir $OUTPUT_DATASET_DIR

echo "===================== CREATING PRE-TRAINING DATASETS ====================="
python3 -u prepare_pretraining_datasets.py --output-dir $OUTPUT_DATASET_DIR

echo "===================== CREATING FINE-TUNING DATASETS ====================="
python3 -u prepare_finetuning_datasets.py --output-dir $OUTPUT_DATASET_DIR