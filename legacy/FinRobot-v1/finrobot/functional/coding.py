import os
from typing_extensions import Annotated
from IPython import get_ipython

default_path = "coding/"


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


def _get_safe_path(base_path: str, filename: str) -> str:
    """
    Constructs a safe absolute path and ensures it does not escape the base_path directory.
    """
    base_abs = os.path.abspath(base_path)
    # Join base and filename, then resolve to absolute path
    target_abs = os.path.abspath(os.path.join(base_path, filename))
    # Ensure target starts with the base directory
    # Adding os.sep ensures that e.g. base_path="coding" doesn't allow "coding2/file"
    if not target_abs.startswith(base_abs + os.sep) and target_abs != base_abs:
        raise ValueError("Invalid path: Path traversal detected.")
    return target_abs


class CodingUtils:  # Borrowed from https://microsoft.github.io/autogen/docs/notebooks/agentchat_function_call_code_writing

    def list_dir(directory: Annotated[str, "Directory to check."]) -> str:
        """
        List files in choosen directory.
        """
        safe_dir = _get_safe_path(default_path, directory)
        files = os.listdir(safe_dir)
        return str(files)

    def see_file(filename: Annotated[str, "Name and path of file to check."]) -> str:
        """
        Check the contents of a chosen file.
        """
        safe_file_path = _get_safe_path(default_path, filename)
        with open(safe_file_path, "r") as file:
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
        safe_file_path = _get_safe_path(default_path, filename)
        with open(safe_file_path, "r+") as file:
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
        safe_file_path = _get_safe_path(default_path, filename)
        directory = os.path.dirname(safe_file_path)
        os.makedirs(directory, exist_ok=True)
        with open(safe_file_path, "w") as file:
            file.write(code)
        return "File created successfully"
