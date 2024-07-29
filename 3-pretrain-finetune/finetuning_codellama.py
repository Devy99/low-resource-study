"""Script to fine-tune CodeLlama model on a custom dataset.
Sources:
- https://github.com/meta-llama/llama-recipes/blob/main/src/llama_recipes/finetuning.py
- https://github.com/meta-llama/llama-recipes/blob/main/src/llama_recipes/datasets/samsum_dataset.py
- https://github.com/meta-llama/llama-recipes/blob/main/src/llama_recipes/datasets/alpaca_dataset.py
- https://github.com/meta-llama/llama-recipes/blob/main/src/llama_recipes/datasets/grammar_dataset/grammar_dataset.py
- https://github.com/salesforce/CodeT5/blob/main/CodeT5%2B/tune_codet5p_seq2seq.py
- https://github.com/salesforce/CodeT5/blob/main/CodeT5%2B/instruct_tune_codet5p.py
- https://github.com/ragntune/code-llama-finetune/blob/main/fine-tune-code-llama.ipynb
- https://huggingface.co/docs/transformers/main/model_doc/code_llama
- https://huggingface.co/codellama/CodeLlama-7b-hf
- https://huggingface.co/docs/transformers/main/model_doc/llama
- https://arxiv.org/pdf/2308.12950.pdf
"""

import os
import pprint
import argparse

import torch
from transformers import CodeLlamaTokenizerFast, LlamaForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from datasets import load_dataset


def run_training(args, train_data, model, tokenizer):
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        save_strategy="epoch",
        do_train=True,
        bf16=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, padding=True)
    )

    trainer.train()

def load_tokenize_data(args, tokenizer):

    # Load dataset
    dataset = load_dataset("json", data_files=args.train_data, split="train", keep_default_na=False)

    # Tokenize dataset
    bos_token = [tokenizer.bos_token_id]
    eos_token = [tokenizer.eos_token_id]
    eot_token = tokenizer(tokenizer.eot_token)["input_ids"]
    
    def preprocess_single(example):
        input = bos_token + tokenizer(example[args.source_column])["input_ids"]
        target = tokenizer(example[args.target_column])["input_ids"] + eot_token + eos_token
        input_ids = input + target
        attention_mask = [1] * len(input_ids)
        labels = [-100] * len(input) + target

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    def discard_long_sample(sample):
        input_ids = len(sample["input_ids"])
        return input_ids <= args.max_source_len

    num_before_filter = len(dataset)
    train_data = dataset.map(
        preprocess_single,
        # batched=True,
        remove_columns=dataset.column_names,
        num_proc=args.num_proc,
    ).filter(
        discard_long_sample,
        num_proc=args.num_proc,
    )

    num_after_filter = len(train_data)
    print(f"Removed {num_before_filter - num_after_filter} samples")
    return train_data


def main(args):

    argsdict = vars(args)
    print(pprint.pformat(argsdict))

    # Load and set up tokenizer
    tokenizer = CodeLlamaTokenizerFast.from_pretrained(args.model_name_or_path)
    tokenizer.add_bos_token = False
    tokenizer.add_eos_token = False
    tokenizer.add_special_tokens({"pad_token": "<pad>"})

    # Load and tokenize dataset
    train_data = load_tokenize_data(args, tokenizer)

    # Load model
    model = LlamaForCausalLM.from_pretrained(
        args.model_name_or_path,
        torch_dtype=torch.bfloat16,
    )
    model.resize_token_embeddings(len(tokenizer))

    # Run training
    run_training(args, train_data, model, tokenizer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune CodeLlama model")
    parser.add_argument("--model", default="meta-llama/CodeLlama-7b-hf", type=str, help="Model name")
    parser.add_argument("--model_name_or_path", default="meta-llama/CodeLlama-7b-hf", type=str, help="Model path")
    parser.add_argument("--output_dir", type=str, help="Output directory")
    parser.add_argument("--train_data", type=str, help="Path to training data")
    parser.add_argument("--max_source_len", default=2048, type=int, help="Maximum sample length")
    parser.add_argument("--source_column", default="instruction", type=str, help="Source column")
    parser.add_argument("--target_column", default="output", type=str, help="Target column")
    parser.add_argument("--batch_size", default=1, type=int, help="Batch size")
    parser.add_argument("--epochs", default=10, type=int, help="Number of epochs")
    parser.add_argument("--num_proc", default=128, type=int, help="Number of processes")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    main(args)