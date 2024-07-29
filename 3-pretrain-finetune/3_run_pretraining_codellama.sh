#!/bin/bash

# Verify that there are enough GPUs available to run the benchmark on separate GPUs
MIN_GPUS=2
GPU_NUMBER=$1
if [ -z "$GPU_NUMBER" ] || [ "$GPU_NUMBER" -lt 0 ] || [ "$GPU_NUMBER" -gt $(($MIN_GPUS - 1)) ]; then
    echo "Please provide a valid GPU number (0-1) as parameter."
    exit 1
fi

LANGUAGES=("r" "racket")
LANGUAGE=${LANGUAGES[$GPU_NUMBER]}

MODEL_PATH=$2
MODEL_LABEL=$(echo $MODEL_PATH | cut -d'/' -f 2)
DATA_PATH="./datasets/pretraining/${LANGUAGE}_pretraining_dataset.jsonl"
OUTPUT_PATH="./checkpoints/${MODEL_LABEL}/pretraining/${LANGUAGE}_pretraining"
mkdir -p $OUTPUT_PATH

python3 -u finetuning_codellama.py \
    --model_name_or_path="$MODEL_PATH"  \
    --max_source_len="2048" \
    --train_data="$DATA_PATH" \
    --batch_size="1" \
    --epochs="3" \
    --output_dir="$OUTPUT_PATH" \
    --num_proc="32"