# [Replication Package] Enhancing Code Generation for Low-Resource Languages: No Silver Bullet

## Introduction
This project repository includes the scripts for replicating our work *"Enhancing Code Generation for Low-Resource Languages: No Silver Bullet"*. In this study, we compare and suggest different approaches for improving the code generation capabilities of state-of-the-art deep learning models. Below is a step-by-step guide for installing the necessary dependencies and reproducing our findings.

## Contents 
1. [Prerequisites](#prerequisites)
2. [Datasets and materials](#datasets-and-materials)
3. [Replication of the results](#replication-of-the-results)

## Prerequisites
This repository contains scripts written and tested in the following languages:
- **Python** (tested on version 3.10.14)
- **R** (tested on version 4.4.0)

Evaluating and testing the model generations requires the usage of Docker containers. We run our experiments with the following version:
- **Docker**  (tested on version 24.0.7)

We employed AppleScript files to conduct the Copilot study. Hence, an Apple machine and a regular subscription to [Github Copilot](https://github.com/features/copilot) are required to reproduce this experiment. You also need the [Visual Studio Code](https://code.visualstudio.com/) editor and the Copilot plugin correctly installed and configured on your machine. We tested this experiment on the following versions:
- Visual Studio Code (tested on version 1.91.1)
- Copilot plugin (tested on version 1.216.0)

Before running the scripts to automate Copilot completions, setup the system permissions as follows:
```
System Settings > Privacy & Security > Accessibility > Allow Visual Studio Code and Terminal applications
```
The provided scripts are intended solely for research purposes. 


### Package Dependencies
Before running our scripts, we recommend creating a new Python virtual environment and installing the required libraries as follows:
  ```sh
   # Create a new virtual environment
   python3 -m venv venv

   # Activate it
   source venv/bin/activate

   # Install the required packages
   pip3 install -r requirements.txt
   ```
We provide an alternative requirements file, namely [deepseek_requirements.txt](3-pretrain-finetune/deepseek_requirements.txt), to train DeepSeek-Coder models. We strongly recommend using an alternative environment and installing the provided packages before training the aforementioned models.

  ```sh
   # Create DeepSeek-Coder virtual environment
   python3 -m venv deepseek_venv
   source deepseek_venv/bin/activate

   # Install the required packages (from DeepSeek-Coder official repository)
   pip3 install -r deepseek_requirements.txt
   ```

### Software Dependencies
We used the [MultiPL-E](https://github.com/nuprl/MultiPL-E) tool as benchmark for our experiments. Since this project is in continuous evolution, our scripts install the tool from the commit `19a2567` , which is the version used in our experiments. You can find an extensive guide on how to install and use this tool on the [official website](https://nuprl.github.io/MultiPL-E/). While we relied on Docker for models evaluation, you can also use [Podman](https://podman.io/) as a replacement. More details are provided in the [official guidelines](https://nuprl.github.io/MultiPL-E/tutorial.html). We also point out that all the experiments were executed on Linux (inference and fine-tuning) and MacOS (copilot benchmark). Hence, the provided scripts and the containers may not run on different operating systems.

### Hardware 
We conducted our experiments on a cluster featuring the following GPUs:
- 8 NVIDIA A100 (80 GB)
- 32 NVIDIA A40
- 8 NVIDIA A30

It is possible to replicate our experiments with a different hardware infrastructure by adjusting inference and training parameters accordingly (see more in [Training](#training) section).

## Datasets and materials
All datasets and results from this study are available in our [Zenodo repository](https://doi.org/10.5281/zenodo.13128630).

In particular, the repository is structured as follows:
- **prompt-prefixes**: list of prompts prepended to the code generation instruction for the in-context learning experiments (translation examples, translation rules, and few-shot)

- **predictions**: includes model evaluation results for each experiment (baseline, in-context evaluation, fine-tuning, and copilot). Each result is stored in the compatible format with the MultiPL-E tool (Gzip compressed files). In particular, for each model and experiment we provide `*.json.gz` files, which contain the model generations for a specific HumanEval problem, and `*.results.json.gz` files, which contain the status of the test suite execution. Under the `finetuning` directory, we have included the model's predictions on the MultiPL-E benchmark for each fine-tuning epoch. The `best-results` folder, instead, groups the predictions of the best checkpoints, whose performance has been described in the paper.

- **results**: provides all the quantitative results from our work. It divides into the following directories:
    - **accuracies**: includes CSV files containing the pass@1 discussed in our study, organized into subdirectories by model and experiment. In folder `epochs-accuracies`, we provide the performance of the 'fine-tuned only' and 'pre-trained and fine-tuned' models for each epoch.
    - **statistical-analyses**: contains the CSV and PDF files that result from the statistical analyses described in the paper. 
    The PDF containing the results of the statistical tests is also available in [this repository](6-statistical-analysis/rq2_stats_analysis_table.pdf).

At the time of this writing, MultiPL-T datasets can only be accessed by accepting the usage terms via the [official HuggingFace repository](https://huggingface.co/datasets/nuprl/MultiPL-T). Due to this policy, we do not include the authors' datasets in the replication package, but provide the necessary scripts to use them for our use cases (see [Datasets generation](#datasets-generation) section for more information).


## Replication of the results
This repository is organized into progressively numbered folders, each representing a different experiment. We recommend executing the scripts in the provided order. Also, each directory contains bash files to aid the correct replication of our scripts. Again, the filenames suggest the  execution order of the scripts. Below, we describe some key experiments contained in this repository.

### Inference
Folders `1-base-benchmark`, `2-context-benchmark`, and `4-finetuned-benchmark` provide the scripts for evaluating base models and their fine-tuned versions. Below is an example of how to run the evaluation scripts:
```sh
# You must launch the script with the following format:
# bash <experiment_script> <language_id> <model_path>
# Experiment scripts: one of the inference scripts provided in the mentioned folders
# Language id: the index of the language in the LANGUAGES array. It defines on which language the model must be evaluated
# Model path: the model to evaluate. It can either be a model on HuggingFace or a checkpoint locally stored on your machine

# E.g., for baseline evaluation with DeepSeek-Coder 1.3B Instruct on the Julia benchmark:
bash 1_run_benchmark.sh 1 deepseek-ai/deepseek-coder-1.3b-instruct
```
Before launching the scripts in `4-finetuned-benchmark`, update the `CHECKPOINTS` list with the names of the checkpoints to evaluate from the fine-tuning stage (folder `3-pretrain-finetune`).

The evaluation of these models relies on the MultiPL-E Benchmark tool, automatically installed through our scripts (see section [Software Dependencies](#software-dependencies)). Before evaluating the model generations, verify that the Docker process is correctly running.

### Datasets generation
File [1_prepare_datasets.sh](3-pretrain-finetune/1_prepare_datasets.sh) contains the scripts used to generate the pre-training and fine-tuning datasets for this study. As mentioned above, we start from the MultiPL-T datasets and adapt them for our use cases. Below are the steps required to re-create the datasets used in our experiments:

- Go to the [MultiPL-T HuggingFace repository](https://huggingface.co/datasets/nuprl/MultiPL-T) and accept their usage terms. This would allow access to their datasets.

- Run the [1_prepare_datasets.sh](3-pretrain-finetune/1_prepare_datasets.sh) script from the terminal. Since the visibility of MultiPL-T datasets is restricted, you must provide a valid [HuggingFace token](https://huggingface.co/docs/hub/security-tokens) and run the script as follows:
    ```sh
    bash 1_prepare_datasets.sh <HF_ACCESS_TOKEN>
    ```

As a result, it will generate the `datasets` folder containing the MultiPL-T Python functions and their translations in the target low-resource languages (`translated` directory). In addition, it will generate:
- the `pretraining` directory, which contains the datasets for the pre-training objective experiment. Each JSON element contains the "instruction" and "output" keys, which are provided in input during model training.
- the `finetuning` folder, containing datasets for fine-tuning models on low-resource languages (R and Racket). The JSON items follow the same schema seen for the translation pretraining objective.

### Training
To train CodeLlama and DeepSeek-Coder models, we used the scripts in folder [3-pretrain-finetune](3-pretrain-finetune). As mentioned in the [Package Dependencies](#package-dependencies) section, we recommend running DeepSeek-Coder training in a separate environment, complying with the [official model specifications](https://github.com/deepseek-ai/DeepSeek-Coder/blob/main/requirements.txt).

To run these scripts, you must specify the model name and the training dataset as shown below:
```sh
# You must launch the script with the following format:
# bash <experiment_script> <dataset_id> <model_path>
# Experiment scripts: one of the pre-training / fine-tuning scripts provided in 3-pretrain-finetune folder
# Dataset id: the index of the language in the LANGUAGES array. It automatically fetch the training dataset.
# Model path: the model you want to train. It can either be a model on HuggingFace or a checkpoint locally stored on your machine

# For example:
bash 2_run_only_finetuning_codellama 0 codellama/CodeLlama-7b-Instruct-hf
```

In case you want to run these scripts on different GPUs, you may need to modify the training batch size or the [DeepSpeed configuration](3-pretrain-finetune/configs/ds_config_zero3.json) accordingly with your hardware infrastructure.



### Copilot experiment
Folder [5-copilot-study](5-copilot-study) contains the scripts to reproduce the Copilot experiment. [1_setup_experiment.sh](5-copilot-study/1_setup_experiment.sh) script generates 50 separate folders, each containing the docstring and the signature of an HumanEval problem and a prompt prefix in case of in-context learning study. Next, you can run the [2_run_copilot.sh](5-copilot-study/2_run_copilot.sh) script to launch Copilot on the generated files. Before running the scripts, ensure that all of the [mentioned dependencies](#prerequisites) are satisfied.