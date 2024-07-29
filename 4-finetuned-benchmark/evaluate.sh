#!/bin/bash

MODEL_NAME=$1
BENCHMARK_DATASET=$2
LANGUAGE=$3
TEMPERATURE=$4
BATCH_SIZE=$5
COMPLETION_LIMIT=$6
MAX_TOKENS=$7
PROMPT_PREFIX=${8}
LABEL=${9}
RESULTS_DIR=${10}
TOKENIZER=${11}

echo "Running benchmark with the following parameters:"
echo "Model name: $MODEL_NAME, Benchmark dataset: $BENCHMARK_DATASET, Language: $LANGUAGE, Temperature: $TEMPERATURE, Batch size: $BATCH_SIZE, Completion limit: $COMPLETION_LIMIT, Max tokens: $MAX_TOKENS, Prompt prefix: $PROMPT_PREFIX, Label: $LABEL, Results dir: $RESULTS_DIR, Tokenizer: $TOKENIZER"

OUTPUT_DIR="${RESULTS_DIR}/${LANGUAGE}_benchmark_temperature_${TEMPERATURE}_$LABEL"
mkdir -p $OUTPUT_DIR

# Run the model generation script
echo "Running model generation script..."
python3 -u MultiPL-E/automodel.py \
        --name $MODEL_NAME \
        --tokenizer_name $TOKENIZER \
        --root-dataset $BENCHMARK_DATASET \
        --lang $LANGUAGE \
        --temperature $TEMPERATURE \
        --batch-size $BATCH_SIZE \
        --completion-limit $COMPLETION_LIMIT \
        --output-dir-prefix $OUTPUT_DIR \
        --max-tokens $MAX_TOKENS \
        --prompt-prefix "$PROMPT_PREFIX"

# Sanitize the generated completions
NEW_RESULTS_DIR=$(echo $RESULTS_DIR | awk -F'/' '{OFS="/"; $2=$2"_cleaned"; print $0}')
CLEANED_OUTPUT_DIR="${NEW_RESULTS_DIR}/${LANGUAGE}_benchmark_temperature_${TEMPERATURE}_$LABEL"
python3 -u ../utils/clean_completions.py --input_dir $OUTPUT_DIR --language $LANGUAGE --output_dir $CLEANED_OUTPUT_DIR

# Run the evaluation script
echo "Running evaluation script..."
docker run --rm --network none -v ./$CLEANED_OUTPUT_DIR:/$CLEANED_OUTPUT_DIR:rw multipl-e-eval --dir /$CLEANED_OUTPUT_DIR --output-dir /$CLEANED_OUTPUT_DIR --recursive

# Print the results
echo "Printing the results..."

TEMPERATURE_LABEL=$(echo $TEMPERATURE | sed 's/\./_/g')
python3 -u ./MultiPL-E/pass_k.py ./$CLEANED_OUTPUT_DIR/* | tee $CLEANED_OUTPUT_DIR/pass_result_temp_${TEMPERATURE_LABEL}.csv
