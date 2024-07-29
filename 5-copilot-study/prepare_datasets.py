import os, datasets

# Load dataset from Hugging Face nuprl/MultiPL-E from a specific split.
subsets = ['humaneval-java', 'humaneval-py', 'humaneval-jl', 'humaneval-lua', 'humaneval-rkt', 'humaneval-r']
experiments = ['baseline', 'mapping_rules', 'transl_examples', 'fewshot']

for subset in subsets:
    for experiment in experiments:
        if (subset == 'humaneval-py' or subset == 'humaneval-java' or subset == 'humaneval-jl' or subset == 'humaneval-lua') and experiment != 'baseline': continue

        # Load dataset from Hugging Face nuprl/MultiPL-E
        dataset = datasets.load_dataset('nuprl/MultiPL-E', subset, split='test', revision='bf4f3c31a1e0a164b7886c9eb04f82534edf4ce9')
        df = dataset.to_pandas()
        print(f"Creating dataset for {subset} - Experiment: {experiment}")

        # Create directory if it does not exist
        dir_name = 'prompts'
        os.makedirs(dir_name, exist_ok=True)
        df.to_json(f'{dir_name}/{subset}.json', orient='records', lines=True)

        # Save each prompt in a single file
        backup_dir, completions_dir = f'{subset}-backup-{experiment}', f'{subset}-completions-{experiment}'
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(completions_dir, exist_ok=True)

        extension =  subset.split('-')[-1] if '-' in subset else subset

        # Load prompt prefix from prompts_prefix dir
        prefix = ''
        if experiment != 'baseline':
            prefix_dir = 'prompts_prefix'
            file = f'python_{extension}_{experiment}.txt' if experiment != 'fewshot' else f'{extension}_{experiment}.txt'
            prefix = open(f'{prefix_dir}/{file}', 'r').read()

        for idx, row in df.iterrows():
            # Create completion file
            filename = f'{completions_dir}/{row["name"]}.{extension}'
            absolute_repo_path = os.path.abspath(filename)
            to_write = f"{prefix}{row['prompt']}"
            if not to_write.endswith('\n'):
                to_write += '\n'

            with open(f'{completions_dir}/{row["name"]}.{extension}', 'w') as f:
                f.write(to_write)
                f.close()
            with open(f'{backup_dir}/{row["name"]}.{extension}', 'w') as f:
                f.write(to_write)
                f.close()

            # Create Apple Scripts
            apple_script = \
        f"""tell application "Visual Studio Code"
        activate
        open "{absolute_repo_path}"
        delay 3.0
        tell application "System Events" to tell process "Visual Studio Code"
            delay 2.0
            key code 125 using command down # Open the file and go to the end
            delay 1.0
            key code 51 # Backspace 
            delay 1.0
            key code 36 # Press Enter to trigger copilot
            delay 7.0
            key code 48 # Accept suggestion with Tab
            key code 48 # Do again in case of multiple suggestions
            delay 1.0
            key code 49  # Add Space
            delay 1.0
            key code 51 # Backspace to remove it and trigger copilot again
            delay 4.0
            key code 48 # Accept the suggestion with Tab    
            delay 1.0
            keystroke "s" using command down # Save code
            delay 1.0
            keystroke "w" using command down # Quit window
            delay 1.0
            keystroke "q" using command down # Quit VSCode
            delay 1.0
        end tell
        end tell
        """
            with open(f'{completions_dir}/{row["name"]}.applescript', 'w') as f:
                f.write(apple_script)
                f.close()

            