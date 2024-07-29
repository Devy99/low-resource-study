import pandas as pd

# Read the CSV file
df = pd.read_csv('rq2_stats_analysis.csv')

# Mapping of model names
model_name_mapping = {
    "deepseek-1.3b": "DeepSeek Coder 1B",
    "deepseek-6.7b": "DeepSeek Coder 7B",
    "deepseek-33b": "DeepSeek Coder 33B",
    "codellama-7b": "Code Llama 7B",
    "codellama-13b": "Code Llama 13B",
    "copilot": "GitHub Copilot"
}

language_name_mapping = {
    "r": "R",
    "rkt": "Racket"
}

technique_name_mapping = {
	"baseline": "Baseline",
	"finetune": "Fine-tuning -- Code Generation",
	"pretrain-finetune": "Pre-training \\& Fine-tuning -- Code Translation and Generation",
	"icl-fewshot": "In-context Learning -- Few-shot Examples",
	"icl-translation": "In-context Learning -- Translation Examples",
	"icl-rules": "In-context Learning -- Translation Rules"
}

# Function to format the OR and p-value
def format_or_pvalue(row):
	or_value = row['OR']
	p_value = row['p.value']
	
	# Swap techniques if OR < 1
	if or_value < 1:
		row['technique1'], row['technique2'] = row['technique2'], row['technique1']
		or_value = 1 / or_value
	
	# Round OR to two decimals
	row['OR'] = f"{or_value:.2f}"
	
	# Format p-value
	if p_value < 0.001:
		row['p.value'] = "$<$0.001"
	else:
		row['p.value'] = f"{p_value:.3f}"
	
	return row

# Sort the DataFrame by technique1 and technique2
df = df.sort_values(by=['technique1', 'technique2'])

# Apply formatting to each row
df = df.apply(format_or_pvalue, axis=1)

# Replace model, language, and technique names
df['model'] = df['model'].replace(model_name_mapping)
df['lng'] = df['lng'].replace(language_name_mapping)
df['technique1'] = df['technique1'].replace(technique_name_mapping)
df['technique2'] = df['technique2'].replace(technique_name_mapping)

# Function to format a row as LaTeX
def format_row(row):
	if row['p.value'] == "$<$0.001" or float(row['p.value']) < 0.05:
		return f"\\textbf{{{row['model']}}} & \\textbf{{{row['lng']}}} & \\textbf{{{row['technique1']}}} & \\textbf{{{row['technique2']}}} & \\textbf{{{row['OR']}}} & \\textbf{{{row['p.value']}}} \\\\"
	else:
		return f"{row['model']} & \\textbf{{{row['lng']}}} & {row['technique1']} & {row['technique2']} & {row['OR']} & {row['p.value']} \\\\"

# Create LaTeX table
latex_table = """\\documentclass[preview,border=1cm]{standalone}
\\usepackage{graphicx}
\\usepackage[margin=0cm]{geometry}
\\usepackage{booktabs}
\\begin{document}
\\begin{table}
\\centering
\\resizebox{\\textwidth}{!}{
\\begin{tabular}{llllrr}
\\toprule
\\textbf{Model} & \\textbf{Language} & \\textbf{Technique} 1 & \\textbf{Technique} 2 & \\textbf{OR} & \\textbf{$p$-value} \\\\
\\midrule"""

previous_technique1 = ""
previous_technique2 = ""
for _, row in df.iterrows():
	if previous_technique1 == "":
		pass
	elif row['technique1'] == previous_technique1 and row['technique2'] == previous_technique2:
		pass
	elif row['technique1'] == previous_technique2 and row['technique2'] == previous_technique1:
		pass
	elif row['technique1'] != previous_technique1 or row['technique1'] != previous_technique2 or row['technique2'] != previous_technique1 or row['technique2'] != previous_technique2:
		latex_table += "\\hline\n"
	
	latex_table += format_row(row) + "\n"

	previous_technique1 = row['technique1']
	previous_technique2 = row['technique2']
	

latex_table += """\\bottomrule
\\end{tabular}
}
\\end{table}
\\vspace{3cm}
\\end{document}"""

# Write LaTeX table to file
with open('rq2_stats_analysis_table.tex', 'w') as f:
	f.write(latex_table)

print("LaTeX table created successfully.")