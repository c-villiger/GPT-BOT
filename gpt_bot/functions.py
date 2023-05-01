import os
import openai
import sys
import subprocess
import re
import pkg_resources
from tabulate import tabulate
from termcolor import colored
import shutil



# Retrieve API key
with open("api_key.txt", "r") as file:
    api_key = file.read().strip()

openai.api_key = api_key


def prompt_openai_api(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message['content'].strip()


def generate_subtasks(task_description, script_type):

    prompt = f"Given the task: '{task_description}', please provide a list of subtasks to complete the the task. Please try to do as much as sensibly possible in one subtask.\
        Structure the subtasks such that each one can be completed in the scope of one code function. Please number the subtasks and do not make subpoints for each subtask."
    subtasks_str = prompt_openai_api(prompt)
    subtasks = [subtask[2:] if subtask.startswith(
        '- ') else subtask for subtask in subtasks_str.split('\n')]
    return [subtask.strip() for subtask in subtasks if subtask.strip()]


def write_code_to_file(name, filename, code):
    workspace_directory = "workspace"
    project_directory = os.path.join(workspace_directory, name)

    if not os.path.exists(workspace_directory):
        os.makedirs(workspace_directory)

    if not os.path.exists(project_directory):
        os.makedirs(project_directory)

    file_path = os.path.join(project_directory, filename)
    with open(file_path, 'w') as file:
        file.write(code)


def read_task_description(file_path):
    task_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split(': ', 1)
            task_dict[key] = value
    return task_dict


def extract_function_and_return_var(code_snippet):
    function_name_pattern = re.compile(r"^\s*def\s+(\w+)\s*\((.*?)\)\s*:")
    return_var_pattern = re.compile(r"^\s*return\s+(\w+)")

    function_name = None
    return_var = None
    function_params = ""

    for line in code_snippet.split('\n'):
        if not function_name:
            match = function_name_pattern.match(line)
            if match:
                function_name = match.group(1)
                function_params = match.group(2) or ""

        if not return_var:
            match = return_var_pattern.match(line)
            if match:
                return_var = match.group(1)

        if function_name and return_var:
            break

    return {f"{function_name}({function_params})": return_var}


def filter_code_lines_functions_only(code):
    lines = code.split('\n')
    filtered_lines = []

    function_started = False
    for line in lines:
        if not function_started and (line.startswith('import') or line.startswith('from')):
            filtered_lines.append(line)
        elif not function_started and line.strip().startswith('def '):
            filtered_lines.append(line)
            function_started = True
        elif function_started and line.strip().startswith('return'):
            filtered_lines.append(line)
            # Add two empty lines after every function
            filtered_lines.append('')
            function_started = False
        elif function_started:
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)


def filter_code_lines(code):
    # Define a regular expression pattern to match common code elements
    pattern = re.compile(r'\s*(import|from|def|class|\w+\s*=|if|\=|\*|\+|_|=|elif|else|for|while|try|except|raise|with|return|append|print|\(|\)|\[|\]|{|}|#|"""|:|"|\'|\(|\))')

    # Split the input string into lines
    lines = code.split('\n')

    # Filter out non-code lines and keep lines between triple quotes
    code_lines = []
    inside_triple_quotes = False
    for line in lines:
        if '"""' in line:
            inside_triple_quotes = not inside_triple_quotes

        if pattern.match(line) or inside_triple_quotes:
            code_lines.append(line)

    # Add two empty lines after each return statement
    formatted_code_lines = []
    for line in code_lines:
        formatted_code_lines.append(line)
        if line.strip().startswith('return'):
            formatted_code_lines.extend(['', ''])

    # Join the filtered and formatted lines into a single string
    filtered_code = '\n'.join(formatted_code_lines)

    return filtered_code

def extract_imports(code):
    imports = []
    lines = code.split('\n')
    for line in lines:
        if line.strip().startswith('import') or line.strip().startswith('from'):
            package_name = re.match(
                r'(?:from|import)\s+([\w\d.]+)', line.strip())
            if package_name:
                top_level_package = package_name.group(1).split('.')[0]
                imports.append(top_level_package)
    return list(set(imports))


def write_requirements_file(name, imports):
    workspace_directory = os.path.join("workspace", name)
    requirements_path = os.path.join(workspace_directory, "requirements.txt")

    import_to_package_map = {
        "sklearn": "scikit-learn",
        "numpy": "numpy",
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "seaborn": "seaborn",
        "scipy": "scipy",
        "statsmodels": "statsmodels",
        "torch": "torch",
        "tensorflow": "tensorflow",
        "keras": "keras",
        "plotly": "plotly",
        "dash": "dash",
        "streamlit": "streamlit",
        "pytorch-lightning": "pytorch-lightning",
        "fastapi": "fastapi",
        "transformers": "transformers",
        "spacy": "spacy",
        "gensim": "gensim",
        "nltk": "nltk",
        "openai": "openai",
        "huggingface-hub": "huggingface-hub",
        "wandb": "wandb",
        "sktime": "sktime",
        # Add more mappings as needed
    }

    existing_requirements = set()
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as file:
            for line in file:
                existing_requirements.add(line.strip().split('==')[0])

    with open(requirements_path, 'a') as file:
        for import_name in imports:
            # Skip the 'random' module -> otherwise will lead to error
            if import_name == "random":
                continue

            package_name = import_to_package_map.get(import_name, import_name)
            if package_name not in existing_requirements:
                try:
                    version = pkg_resources.get_distribution(
                        package_name).version
                    file.write(f"{package_name}\n") #file.write(f"{package_name}=={version}\n")
                except pkg_resources.DistributionNotFound:
                    file.write(f"{package_name}\n")
                existing_requirements.add(package_name)


def reorder_imports(code):
    import_lines = []
    other_lines = []
    lines = code.split('\n')
    existing_imports = set()

    for line in lines:
        if line.strip().startswith('import') or line.strip().startswith('from'):
            # Remove all leading tabs
            line = line.lstrip('\t').lstrip(' ')
            # Check if import already exists
            if line not in existing_imports:
                import_lines.append(line)
                existing_imports.add(line)
        else:
            other_lines.append(line)

    reordered_code = '\n'.join(
        ['"""\nImports\n"""'] + import_lines + ['\n\n\n"""\nFunctions\n"""'] + other_lines)

    return reordered_code


def remove_superfluous_blank_lines(code):
    lines = code.split('\n')
    new_lines = []
    num_blank_lines = 0
    for line in lines:
        if line.strip() == "":
            num_blank_lines += 1
            if num_blank_lines <= 3:
                new_lines.append(line)
        else:
            num_blank_lines = 0
            new_lines.append(line)
    return "\n".join(new_lines)


def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def extract_erroneous_function(error_message):
    """
    Extracts the entire erroneous function from the error message.

    Args:
        error_message (str): The error message.

    Returns:
        str: The erroneous function as a string.
    """
    match = re.search(r"File \"(.+)\", line (\d+), in (.+)", error_message)
    if match:
        file_path = match.group(1)
        line_number = int(match.group(2))
        function_name = match.group(3)
        function_pattern = re.compile(rf"def {function_name}\(")
        end_pattern = re.compile(r"^def |^class ")

        with open(file_path, "r") as file:
            lines = file.readlines()
            function_lines = []
            inside_function = False
            for i, line in enumerate(lines):
                if function_pattern.search(line):
                    inside_function = True
                if inside_function:
                    function_lines.append(line)
                    if i + 1 < len(lines) and end_pattern.search(lines[i + 1]):
                        break

            if function_lines:
                return ''.join(function_lines)

    return None


def run_main_script_and_check_error(name, filename, language):
    # Copy the create_requirements_file.bat file to the subfolder
    subfolder_path = os.path.join("workspace", name)

    if language == "python":
        print_boxed_header("Updating dependencies...", "white")

        # Update all packages in the requirements file
        requirements_file = os.path.abspath(
            os.path.join(subfolder_path, "requirements.txt"))

        update_requirements_command = [
            "pip", "install", "--upgrade", "-r", requirements_file]

        subprocess.run(update_requirements_command, cwd=subfolder_path)

        print_boxed_header("Dependencies updated.", "white")

    script_path = os.path.join(subfolder_path, filename)

    while True:

        # result = subprocess.Popen([sys.executable, script_path],
        #                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        result = subprocess.run([sys.executable, os.path.join(
            subfolder_path, filename)], capture_output=True, text=True)

        if result.returncode != 0:
            error_message = result.stderr.strip()
            error_type = "Error" if "Traceback" not in error_message else "Exception"
            print_boxed_header(f"An {error_type} occurred:", "red")
            print(error_message)

            # Extract the erroneous function
            erroneous_function = extract_erroneous_function(error_message)
            print(erroneous_function)

            if erroneous_function:
                # Prompt the erroneous function and error message to the OpenAI API
                prompt = f"An error occurred in the following function:\n\n{erroneous_function}\nError message:\n{error_message}\nHow can you fix this error?"
                print(f"\nPrompt:\n{prompt}")

                # Replace this with your actual API call
                fixed_function = prompt_openai_api(prompt)
                if fixed_function:
                    # Replace the erroneous function with the corrected one
                    with open(script_path, "r") as file:
                        lines = file.readlines()
                    with open(script_path, "w") as file:
                        replaced = False
                        for line in lines:
                            if erroneous_function.splitlines()[0].strip() in line and not replaced:
                                file.write(fixed_function + "\n")
                                replaced = True
                            else:
                                file.write(line)
                else:
                    break
        else:
            print_boxed_header(f"No error occurred. Output:", "green")

            # Read the output from the subprocess
            stdout, stderr = result.communicate()

            # Print the output
            print(stdout.decode())
            print(stderr.decode())
            break



"""
Functions for graphics
"""

def print_boxed_header(header, color):
    header_length = len(header)
    box_top = "╒" + "═" * (header_length + 2) + "╕"
    box_middle = f"│ {header} │"
    box_bottom = "╘" + "═" * (header_length + 2) + "╛"

    print(colored(box_top, color))
    print(colored(box_middle, color))
    print(colored(box_bottom, color))