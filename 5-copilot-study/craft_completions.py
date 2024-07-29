import os, json, gzip, pandas as pd

# Load dataset from Hugging Face nuprl/MultiPL-E from a specific split. Experiment possible values: '', 'mapping_rules' and 'transl_examples'
dirs = ['copilot_study_1', 'copilot_study_2', 'copilot_study_3', 'copilot_study_4', 'copilot_study_5', 'copilot_study_6', 'copilot_study_7', 'copilot_study_8', 'copilot_study_9', 'copilot_study_10', 'copilot_study_11', 'copilot_study_12', 'copilot_study_13', 'copilot_study_14', 'copilot_study_15', 'copilot_study_16', 'copilot_study_17', 'copilot_study_18', 'copilot_study_19', 'copilot_study_20']
subsets = ['humaneval-java', 'humaneval-py', 'humaneval-jl', 'humaneval-lua', 'humaneval-rkt', 'humaneval-r']
experiments = ['baseline', 'mapping_rules', 'transl_examples', 'fewshot']

for subset in subsets:
    for experiment in experiments:
        if (subset == 'humaneval-py' or subset == 'humaneval-java' or subset == 'humaneval-jl' or subset == 'humaneval-lua') and experiment != 'baseline': continue

        # Prompts json list
        prompts_filepath = f'prompts/{subset}.json'
        df = pd.read_json(prompts_filepath, lines=True)

        # Create output dir 
        output_dir = f'./completions/copilot/{subset}-completions-{experiment}/{subset}-completions-{experiment}'
        os.makedirs(output_dir, exist_ok=True)

        # Save each prompt in a single file
        backup_dir, completions_dir = f'{subset}-backup-{experiment}', f'{subset}-completions-{experiment}'
        extension =  subset.split('-')[-1] if '-' in subset else subset

        # Get all the files in the completions dir
        first_backup_dir = f'{dirs[0]}/{backup_dir}'
        files = [f for f in os.listdir(first_backup_dir) if f.endswith(f'.{extension}')]
        for file in files:
            backup_filepath = f'{first_backup_dir}/{file}'
            with open(backup_filepath, 'r') as f:
                backup = f.read()

            backup_lines = backup.strip().split('\n')
            last_index = len(backup_lines) - 1

            completions = []
            for dir in dirs:
                completion_filepath = f'{dir}/{completions_dir}/{file}'
                with open(completion_filepath, 'r') as f:
                    completion = f.read()

                # Take only the completion part
                completion_lines = completion.split('\n')[last_index+1:]
                body = '\n'.join(completion_lines)

                if not body.strip():
                    print(f'Empty completion for {completion_filepath} in {dir}')
                    exit(1)

                completions.append(body)

            filename_no_ext = file.split('.')[0]

            # Craft completion as in the MultiPL-E dataset. We also add a fake temperature, top_p and max_tokens values to respect the schema
            row = df[df['name'] == filename_no_ext]
            row = row.iloc[0]
            row = row.to_dict()
            row['completions'] = completions
            row['temperature'] = 0.2
            row['top_p'] = 0.95
            row['max_tokens'] = 1024

            # Remove the brackets from the tests
            if subset == 'humaneval-java':
                row['tests'] = row['tests'].split('}', 1)[1]

            # Save the completion in a json file and gzip it
            output_filepath = f'{output_dir}/{filename_no_ext}.json'
            with open(output_filepath, 'w') as f:
                json.dump(row, f)
                f.close()

            with open(output_filepath, 'rb') as f_in:
                with gzip.open(f'{output_filepath}.gz', 'wb') as f_out:
                    f_out.writelines(f_in)

            # Remove the json file
            os.remove(output_filepath)


