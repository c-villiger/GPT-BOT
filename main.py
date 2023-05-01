"""
Imports
"""
from tabulate import tabulate
from termcolor import colored
import os

from gpt_bot.functions import read_task_description, generate_subtasks, prompt_openai_api, \
    extract_function_and_return_var, filter_code_lines, reorder_imports, extract_imports, write_requirements_file, \
        remove_superfluous_blank_lines, write_code_to_file, run_main_script_and_check_error, \
        print_boxed_header, delete_files_in_folder



def main():
    """
    Read in task description
    """

    task_description_file = 'task_description.txt'
    task_description_dict = read_task_description(task_description_file)

    """
    Generate script types
    """

    script_types = ["run script"]

    """
    Divide into subtasks
    """
    for script_type in script_types:

        # Generate subtasks for each script type
        subtasks = generate_subtasks(
            task_description_dict['task'], script_type)

        print_boxed_header(f"{script_type.capitalize()} Subtasks:", "white")
        print("----------------------------------------------------------------------------------")
        for task in subtasks:
            print(task)

        code = f""

        function_return_dict = {}

        for index, subtask in enumerate(subtasks):

            code_prompt = f"Write a single {task_description_dict['language']} function for the following subtask. Please ONLY give the function and no additional text response and end every function with a return statement: '{subtask}'. \
                This is a list of all the subtasks that have been generated so far:\n\n {subtasks} \n\n. \
                Please stay consistent with the function names and return variables, according to the previous subtasks, if they were already generated. Do NOT generate additional text, only the code functions.\
                Here are the function names and return variables that have been generated so far:\n\n {function_return_dict} \n\n. \
                If it is empty, simply assume that this is the first subtask. Please make an error in every function for testing puporses."

            code_snippet = prompt_openai_api(code_prompt)

            func_and_var = extract_function_and_return_var(code_snippet)
            function_return_dict.update(func_and_var)

            code += f"\n{code_snippet}\n"

        language_to_extension = {
            "python": ".py",
            "matlab": ".m",
            "r": ".R",
            "batch": ".bat",
            # Add more languages and their extensions here
        }

        extension = language_to_extension.get(
            task_description_dict['language'].lower(), "")
        filename = f"{script_type.replace(' ', '_')}{extension}"

        # Delete all existing files with the folder
        subfolder_path = os.path.join("workspace", task_description_dict['name'])
        delete_files_in_folder(subfolder_path)

        write_code_to_file(
            task_description_dict['name'], 'full_code', code)

        # Filter the code to omit non-code lines
        filtered_code = filter_code_lines(code)

        # Rearrange imports in case of python
        if task_description_dict['language'] == 'python':

            # Reorder imports to the top of the file
            reordered_code = reorder_imports(filtered_code)

            # Extract imports from the code
            imports = extract_imports(reordered_code)

            # Write the imports to the requirements.txt file
            write_requirements_file(task_description_dict['name'], imports)

        # Remove superfluous blank lines
        reordered_code = remove_superfluous_blank_lines(reordered_code)

        # Write the code to a file
        write_code_to_file(
            task_description_dict['name'], filename, reordered_code)
        print_boxed_header(f'Generated {filename}', 'green')

    """
    Run main script and check for errors
    """

    run_main_script_and_check_error(
        task_description_dict['name'], filename, task_description_dict['language'])


if __name__ == "__main__":
    main()
