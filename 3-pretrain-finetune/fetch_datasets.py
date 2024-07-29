import os, argparse, datasets

def get_argparser() -> argparse.ArgumentParser:
    """
    Get the configured argument parser
    """
    parser = argparse.ArgumentParser(description='optional arguments')
    parser.add_argument('--output-dir', '-o',
                        metavar='PATH',
                        dest='out_dir',
                        required=False,
                        type=str,
                        default='output',
                        help='Name of the directory where to save the fetched datasets')

    required = parser.add_argument_group('required arguments')
    required.add_argument('--token', '-t',
                        metavar='VALUE',
                        dest='token',
                        required=True,
                        type=str,
                        help='HuggingFace token to access the datasets')

    return parser

if __name__ == '__main__':  

    # Read arg parameters
    parser = get_argparser()
    args = parser.parse_args()

    # Create output directoryies
    token = args.token
    output_dir = args.out_dir
    if not os.path.exists(os.path.join(output_dir, 'translated')):
        os.makedirs(os.path.join(output_dir, 'translated'))

    # Fetch the python dataset and save it as JSONL file
    print('Fetching python dataset...')
    python_dataset = datasets.load_dataset('nuprl/stack-dedup-python-testgen-starcoder-filter-v2', token=token)
    python_df = python_dataset['train'].to_pandas()
    filepath = os.path.join(output_dir, 'python.jsonl')
    python_df.to_json(filepath, orient='records', lines=True)

    # Load the translated datasets and save these as JSONL files
    translated_dataset = datasets.load_dataset('nuprl/MultiPL-T', token=token)
    splits = translated_dataset.keys()
    for split in splits:
        print(f'Fetching {split} dataset...')
        df = translated_dataset[split].to_pandas()
        filepath = os.path.join(output_dir, 'translated', f'{split}.jsonl')
        df.to_json(filepath, orient='records', lines=True)

    print('Datasets fetched and saved successfully.')