from pygments.lexers import get_lexer_by_name
from pygments.token import Token
import os, argparse, pandas as pd

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

def separate_doc_func(function, lexer, language, target_token=Token.Comment): 
    tokens = list(lexer.get_tokens(function))
    doc_tokens, function_tokens = list(), list()
    # If lang is Racket, skip all the tokens until the target_token
    if language == 'racket':
        for i, t in enumerate(tokens):
            if t[0] in target_token:
                tokens = tokens[i:]
                break
            else:
                doc_tokens.append(t[1])
    # Check the first token starting with a target_token
    if tokens[0][0] not in target_token:
        return '', function
    is_start = True
    for t in tokens:
        if is_start and (t[0] in target_token or t[0] in Token.Text):
            doc_tokens.append(t[1])
        else:
            is_start = False
            function_tokens.append(t[1])
    doc = ''.join(doc_tokens).strip()
    func = ''.join(function_tokens).strip()
    return doc, func


def signature_end_idx_par(lines: list) -> int:
    """
    Find the index of the line closing the method signature.
    It works on the assumption that the first open parenthesis is the start of the method signature.
    """
    stack = list()
    for line_idx, line in enumerate(lines):
        for char in line:
            if char == '(':
                stack.append(line_idx)
            elif char == ')' and stack:
                stack.pop()
                if not stack and line_idx < len(lines) - 1:
                    return line_idx
    return -1

if __name__ == '__main__':  

    # Read arg parameters
    parser = get_argparser()
    args = parser.parse_args()

    output_dir = args.out_dir
    translated_dir = os.path.join(output_dir, 'translated')

    # Create finetuning directory
    finetuning_dir = os.path.join(output_dir, 'finetuning')
    if not os.path.exists(finetuning_dir):
        os.makedirs(finetuning_dir)

    target_token_dict = {
        'julia': Token.Literal.String,
        'lua': Token.Comment,
        'ocaml': Token.Comment,
        'r': Token.Comment,
        'racket': Token.Comment,
    }

    # For each file in the translated directory, separate the docstring from the function
    for file in os.listdir(translated_dir):
        print(f"Processing file: {file}")
        filepath = os.path.join(translated_dir, file)

        # Get the language from the file name
        language = os.path.splitext(file)[0]
        lexer = get_lexer_by_name(language)

        df = pd.read_json(filepath, lines=True)
        functions = df['content'].tolist()

        instructions, responses = list(), list()
        for entry in functions:
            doc, func = separate_doc_func(entry, lexer, language, target_token_dict[language])

            # Get method signature
            lines = func.split('\n')
            if language == 'racket':
                # Workaround to not considerate the first parenthesis
                try:
                    temp_lines = lines.copy()
                    temp_lines[0] = temp_lines[0].split('define', 1)[1]
                    end_idx = signature_end_idx_par(temp_lines)
                except:
                    continue
            else:
                end_idx = signature_end_idx_par(lines)

            signature = '\n'.join(lines[:end_idx+1])
            response = '\n'.join(lines[end_idx+1:])

            instruction = f"{doc}\n{signature}"
            instructions.append(instruction)
            responses.append(response)
        
        df = pd.DataFrame({'instruction': instructions, 'output': responses})
        output_file = os.path.join(finetuning_dir, f'{language}_finetuning.jsonl')
        df.to_json(output_file, orient='records', lines=True)
    
    print('Finetuning datasets prepared successfully.')
