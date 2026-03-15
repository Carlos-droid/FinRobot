import os
from typing_extensions import Annotated
from IPython import get_ipython
from pathlib import Path

default_path = "coding/"

def is_safe_path(base_dir: str, requested_path: str) -> bool:
    """Ensure the requested path resolves to a location strictly within the base_dir."""
    base = Path(base_dir).resolve()
    target = (Path(base_dir) / requested_path).resolve()

    try:
        return target.is_relative_to(base)
    except AttributeError:
        return str(target).startswith(str(base))


class IPythonUtils:

    def exec_python(cell: Annotated[str, "Valid Python cell to execute."]) -> str:
        """
        run cell in ipython and return the execution result.
        """
        ipython = get_ipython()
        result = ipython.run_cell(cell)
        log = str(result.result)
        if result.error_before_exec is not None:
            log += f"\n{result.error_before_exec}"
        if result.error_in_exec is not None:
            log += f"\n{result.error_in_exec}"
        return log

    def display_image(
        image_path: Annotated[str, "Path to image file to display."]
    ) -> str:
        """
        Display image in Jupyter Notebook.
        """
        log = __class__.exec_python(
            f"from IPython.display import Image, display\n\ndisplay(Image(filename='{image_path}'))"
        )
        if not log:
            return "Image displayed successfully"
        else:
            return log


class CodingUtils:  # Borrowed from https://microsoft.github.io/autogen/docs/notebooks/agentchat_function_call_code_writing

    def list_dir(directory: Annotated[str, "Directory to check."]) -> str:
        """
        List files in choosen directory.
        """
        if not is_safe_path(default_path, directory):
            return "Error: Path traversal detected. You can only access files within the 'coding/' directory."
        files = os.listdir(default_path + directory)
        return str(files)

    def see_file(filename: Annotated[str, "Name and path of file to check."]) -> str:
        """
        Check the contents of a chosen file.
        """
        if not is_safe_path(default_path, filename):
            return "Error: Path traversal detected. You can only access files within the 'coding/' directory."
        with open(default_path + filename, "r") as file:
            lines = file.readlines()
        formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
        file_contents = "".join(formatted_lines)

        return file_contents

    def modify_code(
        filename: Annotated[str, "Name and path of file to change."],
        start_line: Annotated[int, "Start line number to replace with new code."],
        end_line: Annotated[int, "End line number to replace with new code."],
        new_code: Annotated[
            str,
            "New piece of code to replace old code with. Remember about providing indents.",
        ],
    ) -> str:
        """
        Replace old piece of code with new one. Proper indentation is important.
        """
        if not is_safe_path(default_path, filename):
            return "Error: Path traversal detected. You can only access files within the 'coding/' directory."
        with open(default_path + filename, "r+") as file:
            file_contents = file.readlines()
            file_contents[start_line - 1 : end_line] = [new_code + "\n"]
            file.seek(0)
            file.truncate()
            file.write("".join(file_contents))
        return "Code modified"

    def create_file_with_code(
        filename: Annotated[str, "Name and path of file to create."],
        code: Annotated[str, "Code to write in the file."],
    ) -> str:
        """
        Create a new file with provided code.
        """
        if not is_safe_path(default_path, filename):
            return "Error: Path traversal detected. You can only access files within the 'coding/' directory."
        directory = os.path.dirname(default_path + filename)
        os.makedirs(directory, exist_ok=True)
        with open(default_path + filename, "w") as file:
            file.write(code)
        return "File created successfully"
