from pygments.lexers import get_lexer_by_name
from pygments.token import Token
import os, re, argparse, pandas as pd

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

    return parser

def get_function_name(code: str, language: str) -> str:
    lexer = get_lexer_by_name(language)
    target_token = Token.Name.Function if language in ['java', 'python', 'lua'] else Token.Name
    tokens = list(lexer.get_tokens_unprocessed(code))
    for (_, token, value) in tokens:
        if token is target_token: return value
    return None

def normalize_function_name(name : str):
    if not name: return None
    modified_string = list(map(lambda x: '_' + x if x.isupper() else x, name))
    split_string = ''.join(modified_string).split('_')
    splits = list(filter(lambda x: x != '', split_string))
    lowercased_function_name = ''.join(splits).lower()
    return lowercased_function_name


def extract_docstring(function, lexer, language, target_token=Token.Comment): 
    tokens = list(lexer.get_tokens(function))
    doc_tokens = list()

    # If lang is Racket, skip all the tokens until the target_token
    if language == 'racket':
        for i, t in enumerate(tokens):
            if t[0] in target_token:
                tokens = tokens[i:]
                break
            else:
                doc_tokens.append(t[1])
    elif language == 'python':
        code_splits = function.split('"""', 2)
        docstring = code_splits[1].strip() if len(code_splits) > 1 else ''
        return clean_docstring(docstring, language)

    # Check the first token starting with a target_token
    if tokens[0][0] not in target_token:
        return ''

    is_start = True
    for t in tokens:
        if is_start and (t[0] in target_token or t[0] in Token.Text):
            doc_tokens.append(t[1])
        else:
            is_start = False

    doc = ''.join(doc_tokens).strip()
    return clean_docstring(doc, language)


def clean_docstring(docstring: str, language: str) -> str:
    """
    Clean the docstring from the language syntax and markdown syntax
    """
    docstring = docstring.strip()
    if not docstring: return ''

    # Remove docstring syntax
    if language == 'python':
        docstring = re.sub(r'"""', '', docstring)
        docstring = re.sub(r"'''", '', docstring)
    elif language == 'lua':
        docstring = re.sub(r'--\[\[', '', docstring)
        docstring = re.sub(r'--\[', '', docstring)
        docstring = re.sub(r'\]\]--', '', docstring)
        docstring = re.sub(r'\]--', '', docstring)
        docstring = re.sub(r'--', '', docstring)
        docstring = re.sub(r' -', '', docstring)
        docstring = re.sub(r'- ', '', docstring)
        docstring = re.sub(r'---', '', docstring)
    elif language == 'julia':
        docstring = re.sub(r'"""', '', docstring)
        docstring = re.sub(r'"', '', docstring)
    elif language == 'r':
        docstring = re.sub(r'#\'', '', docstring)
        docstring = re.sub(r'#', '', docstring)
    elif language == 'ocaml':
        docstring = re.sub(r'\(\*\*', '', docstring)
        docstring = re.sub(r'\*\)', '', docstring)
        docstring = re.sub(r'\*', '', docstring)
    elif language == 'racket':
        docstring = re.sub(r'#\|', '', docstring)
        docstring = re.sub(r'\|#', '', docstring)
        docstring = re.sub(r'\|', '', docstring)
        docstring = re.sub(r'#lang racket', '', docstring)
        docstring = re.sub(r';;', '', docstring)

    return docstring.strip()

if __name__ == '__main__':  

    # Read arg parameters
    parser = get_argparser()
    args = parser.parse_args()

    # Create output directoryies
    output_dir = args.out_dir
    translated_dir = os.path.join(output_dir, 'translated')

    # Create pretraining directory
    pretraining_dir = os.path.join(output_dir, 'pretraining')
    if not os.path.exists(pretraining_dir):
        os.makedirs(pretraining_dir)

    # Retrieve the original dataset and extract the function names and docstrings
    python_lexer = get_lexer_by_name('python')
    python_df = pd.read_json(os.path.join(output_dir, 'python.jsonl'), lines=True)
    python_df['function_name'] = python_df['content'].apply(lambda x: get_function_name(x, 'python'))
    python_df['function_name'] = python_df['function_name'].apply(lambda x: normalize_function_name(x))
    python_df['docstring'] = python_df['content'].apply(lambda x: extract_docstring(x, python_lexer, 'python'))
    python_df['first_sentence'] = python_df['docstring'].apply(lambda x: re.sub(r'\s+', ' ', x[:50]).strip())
    print(f"Python function names: {len(python_df[python_df['function_name'].notnull()])}")
    print(f"Python docstrings: {len(python_df[python_df['docstring'].notnull()])}")

    python_df = python_df[['function_name', 'first_sentence', 'content', 'id']]
    python_df.columns = ['function_name', 'first_sentence', 'python_code', 'python_id']

    # Define the docstring target token for each language
    target_token_dict = {
        'julia': Token.Literal.String,
        'lua': Token.Comment,
        'ocaml': Token.Comment,
        'r': Token.Comment,
        'racket': Token.Comment,
    }

    # Iterate over all files in the translated directory
    for file in os.listdir(translated_dir):
        if file.endswith('.jsonl'):
            language = file.split('.')[0]
            lexer = get_lexer_by_name(language)
            print(f"\nProcessing {file}, language {language}...")

            df = pd.read_json(os.path.join(translated_dir, file), lines=True)
            df['id'] = df.index
            df['function_name'] = df['content'].apply(lambda x: get_function_name(x, file.split('.')[0]))
            df['function_name'] = df['function_name'].apply(lambda x: normalize_function_name(x))
            df['docstring'] = df['content'].apply(lambda x: extract_docstring(x, lexer, language, target_token_dict[language]))
            df['first_sentence'] = df['docstring'].apply(lambda x: re.sub(r'\s+', ' ', x[:50]).strip())

            print(f"{file} function names: {len(df[df['function_name'].notnull()])}")
            print(f"{file} docstrings: {len(df[df['docstring'].notnull()])}")

            # Merge with the python dataframe
            merged_df = df.merge(python_df, on=['function_name', 'first_sentence'], how='left')

            # Drop duplicates by id
            merged_df.drop_duplicates(subset='id', inplace=True)
            print(f"Functions with a corresponding Python method: {len(merged_df[merged_df['python_code'].notnull()])}")

            # Save the pretraining dataset
            output_filepath = os.path.join(pretraining_dir, f'{language}_merged_pretraining_dataset.jsonl')
            merged_df.to_json(output_filepath, orient='records', lines=True)

            # Prepare prompt instruction
            prompt_instruction = f"Translate the following Python function to {language.capitalize()}:\n\n" 
            merged_df['instruction'] = prompt_instruction + merged_df['python_code']
            merged_df['output'] = merged_df['content']

            final_df = merged_df[['instruction', 'output']]
            final_df.drop_duplicates(subset='instruction', inplace=True)
            final_df.dropna(subset=['instruction', 'output'], inplace=True)
            print(f"Unique instructions: {len(final_df)}")

            output_filepath = os.path.join(pretraining_dir, f'{language}_pretraining_dataset.jsonl')
            final_df.to_json(output_filepath, orient='records', lines=True)


