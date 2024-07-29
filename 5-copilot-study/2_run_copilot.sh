#!/bin/bash


SCRIPT_DIRS=(
    "humaneval-java-completions-baseline" "humaneval-py-completions-baseline"
    "humaneval-lua-completions-baseline" "humaneval-jl-completions-baseline"
    "humaneval-r-completions-baseline" "humaneval-rkt-completions-baseline"
    "humaneval-r-completions-mapping_rules" "humaneval-rkt-completions-mapping_rules"
    "humaneval-r-completions-transl_examples" "humaneval-rkt-completions-transl_examples"
    "humaneval-r-completions-fewshot" "humaneval-rkt-completions-fewshot"
)

# Iterate over the experiment directories
for i in {1..20}; do
    EXPERIMENT_DIR="copilot_study_$i"
    echo "Running experiment $EXPERIMENT_DIR"
    cd $EXPERIMENT_DIR

    # Iterate over the script directories
    for SCRIPT_DIR in ${SCRIPT_DIRS[@]}; do
        echo "Running Copilot on $SCRIPT_DIR"
        
        # Run all the .applescript files in the scripts directory
        for script in $SCRIPT_DIR/*.applescript; do
        osascript $script
        done
    done

    echo ""
    cd ..
done