def latex_table_generator():

    import json

    # Load JSON data
    with open('/home/yijia/git-bench/data/meta/GSRBench100_commit_ids.json', 'r') as f:
        data = json.load(f)

    # Function to extract the repository name from the URL
    def get_repo_name(url):
        return url.rstrip('/').split('/')[-1]

    # Sort the data by the repository name extracted from the URL
    sorted_data = sorted(data.items(), key=lambda item: get_repo_name(item[0]))

    # Split the sorted data into two halves
    mid_index = len(sorted_data) // 2
    first_half = sorted_data[:mid_index]
    second_half = sorted_data[mid_index:]

    # Function to generate LaTeX code for a given dataset
    def generate_latex(data, table_name):
        latex_code = f"""
        \\begin{{table*}}
        \\caption{{GitHub Repository Details - {table_name}}}
        \\label{{tab:repo_{table_name}}}
        \\begin{{tabular}}{{|l|l|l|}}
            \\hline
            Repository URL & Commit ID & Branch \\\\
            \\hline
        """

        for url, details in data:
            commit_id = details[0]
            branch = details[1].replace('_', '\\_')
            url = url.replace('_', '\\_')
            url = f"\\url{{{url}}}"
            latex_code += f"    {url} & {commit_id} & {branch} \\\\\n    \\hline\n"

        latex_code += """
        \\end{tabular}
        \\end{table*}
        """
        
        return latex_code

    # Generate LaTeX code for both halves
    latex_code_1 = generate_latex(first_half, "Part 1")
    latex_code_2 = generate_latex(second_half, "Part 2")

    # Save into one file
    with open("table.tex", "w") as file:
        file.write(latex_code_1)
        file.write(latex_code_2)


def move_issues():
    import os
    import shutil

    # Define the source and destination directories
    source_directory = './issues/'
    destination_directory = '/opt/dlami/nvme/backup/GSRBench100/'

    # Ensure the destination directory exists
    os.makedirs(destination_directory, exist_ok=True)

    # Iterate over all files in the source directory
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.json'):
                # Construct full file path
                file_path = os.path.join(root, file)
                # Extract the filename without the .json extension
                filename = os.path.splitext(file)[0]
                # Construct the destination file path
                destination_file_path = os.path.join(destination_directory, filename)
                # Copy the file to the destination directory with the new name
                shutil.copy(file_path, destination_file_path)
                # print(f'cp {file_path} {destination_file_path}')
                print(f'Copied {file} to {destination_file_path}')

