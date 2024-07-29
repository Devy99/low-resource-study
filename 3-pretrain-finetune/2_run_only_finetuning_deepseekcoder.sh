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
DATA_PATH="./datasets/finetuning/${LANGUAGE}_finetuning.jsonl"
OUTPUT_PATH="./checkpoints/${MODEL_LABEL}/finetuning/${LANGUAGE}_finetuning"
mkdir -p $OUTPUT_PATH

deepspeed finetuning_deepseekcoder.py \
    --model_name_or_path $MODEL_PATH \
    --data_path $DATA_PATH \
    --output_dir $OUTPUT_PATH \
    --num_train_epochs 3 \
    --model_max_length 2048 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 4 \
    --evaluation_strategy "no" \
    --save_strategy "epoch" \
    --save_total_limit 100 \
    --learning_rate 2e-5 \
    --warmup_steps 10 \
    --logging_steps 500 \
    --lr_scheduler_type "cosine" \
    --gradient_checkpointing True \
    --deepspeed configs/ds_config_zero3.json \
    --bf16 True