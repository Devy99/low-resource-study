import os
import gzip
import json


def get_model_technique_language(path):
    """
    Extract model, technique, and language from the given path.

    :param path: Path to extract information from.
    :return: Tuple with model, technique, and language.
    """
    # Model:
    if "-7b-" in path:
        model = "codellama-7b"
    elif "-13b-" in path:
        model = "codellama-13b"
    elif "-1.3b-" in path:
        model = "deepseek-1.3b"
    elif "-6.7b-" in path:
        model = "deepseek-6.7b"
    elif "-33b-" in path:
        model = "deepseek-33b"
    elif "Copilot" in path:
        model = "copilot"
    else:
        raise ValueError(f"Unknown model in path: {path}")

    # Technique:
    if "-base-" in path:
        technique = "baseline"
    else:
        raise ValueError(f"Unknown technique in path: {path}")
    
    # Language:
    if "-java-" in path:
        language = "java"
    elif "-py-" in path:
        language = "py"
    elif "-jl-" in path:
        language = "jl"
    elif "-lua-" in path:
        language = "lua"
    elif "-r-" in path:
        language = "r"
    elif "-rkt-" in path:
        language = "rkt"
    else:
        raise ValueError(f"Unknown language in path: {path}")
    
    return model, technique, language


def main():
    folder_path = "./results/rq1"
    output = "rq1_results.csv"

    # Create CSV and add header
    csv_file = open(output, "w")
    csv_file.write("model,technique,language,problem,pass\n")

    # Recursively traverse folder:
    for root, dirs, files in os.walk(folder_path):
        print(f"Processing folder: {root}")
        model, technique, language = None, None, None
        # If folder contains results gz files, process them and update CSV
        for file in files:
            if file.endswith(".gz") and ".results." in file:
                if model is None:
                    model, technique, language = get_model_technique_language(root)
                with gzip.open(os.path.join(root, file), 'rb') as f:
                    # Read content as JSON
                    problem_results = json.loads(f.read())
                    # Add results to CSV
                    for result in problem_results["results"]:
                        csv_file.write(f"{model},{technique},{language},{problem_results["name"]},{1 if result["status"] == "OK" else 0}\n")


if __name__ == "__main__":
    main()