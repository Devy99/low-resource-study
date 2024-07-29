import csv
from collections import Counter


def count_problems(input_file):
    """Count occurrences of each problem in the CSV file."""
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        problem_counts = Counter(row['problem'] for row in reader)
    return problem_counts

def filter_csv(input_file, output_file, problem_counts):
    """Write rows to the output file if their problem count is 1620,
    i.e., (6 languages x 5 techniques x 50 repetitions) +
    (6 languages x 1 Copilot x 20 repetitions)."""
    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if problem_counts[row['problem']] == 1620:
                writer.writerow(row)

def main():
    """Parse arguments and process the CSV file."""
    input_file = "rq1_results.csv"
    output_file = "rq1_results_filtered.csv"

    problem_counts = count_problems(input_file)
    filter_csv(input_file, output_file, problem_counts)

if __name__ == "__main__":
    main()