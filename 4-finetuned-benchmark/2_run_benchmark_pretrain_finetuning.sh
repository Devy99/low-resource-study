#!/bin/bash

# Clone MultiPL-E repository
if [ ! -d "MultiPL-E" ]; then
    echo "Cloning MultiPL-E repository..."
    git clone https://github.com/nuprl/MultiPL-E.git
    cd MultiPL-E
    git checkout 19a25675e6df678945a6e3da0dca9473265b0055
    cd ..
fi

# Setup MultiPL-E docker image
TAG="multipl-e-eval"
IMAGE="ghcr.io/nuprl/multipl-e-evaluation:latest"
if [ "$(docker images -q $IMAGE 2> /dev/null)" == "" ]; then
    echo "Pulling and tagging Multipl-E image..."
    docker pull $IMAGE
    docker tag $IMAGE $TAG
else
    echo "Multipl-E image already set up. Continuing..."
fi

# Verify that there are enough GPUs available to run the benchmark on separate GPUs
MIN_GPUS=2
GPU_NUMBER=$1
if [ -z "$GPU_NUMBER" ] || [ "$GPU_NUMBER" -lt 0 ] || [ "$GPU_NUMBER" -gt $(($MIN_GPUS - 1)) ]; then
    echo "Please provide a valid GPU number (0-1) as parameter."
    exit 1
fi

# Run the benchmark for the selected language and each temperature on human eval dataset
LANGUAGES=("r" "rkt")
LANGUAGES_FULL=("r" "racket")
LANGUAGE=${LANGUAGES[$GPU_NUMBER]}
LANGUAGE_FULL=${LANGUAGES_FULL[$GPU_NUMBER]}

MODEL_PATH=$2
MODEL_LABEL=$(echo $MODEL_PATH | cut -d'/' -f 2)

# Change the checkpoints to the ones from the finetuning
CHECKPOINTS=("name-checkpoint-r" "name-checkpoint-rkt")
CHECKPOINT=${CHECKPOINTS[$GPU_NUMBER]}

MODEL_BASE_PATH="../3-pretrain-finetune/checkpoints/${MODEL_LABEL}/pretrain_finetuning/${LANGUAGE_FULL}_finetuning"
MODEL_NAME="${MODEL_BASE_PATH}/${CHECKPOINT}"

BENCHMARK_DATASET="humaneval"
BATCH_SIZE=20
COMPLETION_LIMIT=50
MAX_TOKENS=1024
PROMPT_PREFIX=""
LABEL="no_context_pretrain_finetuned"

RESULTS_DIR="./results_pretrain_finetuned/$MODEL_LABEL"
mkdir -p $RESULTS_DIR

# Temperature 0.2
echo "Temperature 0.2"
TEMPERATURE=0.2
bash evaluate.sh $MODEL_NAME $BENCHMARK_DATASET $LANGUAGE $TEMPERATURE $BATCH_SIZE $COMPLETION_LIMIT $MAX_TOKENS "$PROMPT_PREFIX" $LABEL $RESULTS_DIR $MODEL_PATH