import os
import sys
import re
from typing_extensions import Annotated
from IPython import get_ipython
from pathlib import Path

# Configuración de ruta base para la ejecución de código
default_path = "coding/"

def _get_safe_path(base_path: str, filename: str) -> Path:
    """
    Construye una ruta absoluta segura y garantiza que no escape 
    del directorio base (prevención de Path Traversal).
    """
    base = Path(base_path).resolve()
    # Unir la ruta base con el archivo solicitado y resolver
    target = (base / filename).resolve()

    # Verificar que el target esté dentro del base
    try:
        if not target.is_relative_to(base):
            raise ValueError(f"Acceso denegado: La ruta '{filename}' está fuera de '{base_path}'")
    except AttributeError: # Fallback para Python < 3.9
        if not str(target).startswith(str(base)):
            raise ValueError(f"Acceso denegado: La ruta '{filename}' está fuera de '{base_path}'")
            
    return target


class IPythonUtils:
    @staticmethod
    def exec_python(cell: Annotated[str, "Valid Python cell to execute."]) -> str:
        """Ejecuta una celda en IPython y devuelve el resultado o el error."""
        ipython = get_ipython()
        if ipython is None:
            return "Error: No se detectó un entorno IPython activo."
            
        result = ipython.run_cell(cell)
        log = str(result.result) if result.result is not None else ""
        
        if result.error_before_exec is not None:
            log += f"\nError antes de ejecución: {result.error_before_exec}"
        if result.error_in_exec is not None:
            log += f"\nError en ejecución: {result.error_in_exec}"
        return log

    @staticmethod
    def display_image(
        image_path: Annotated[str, "Path to image file to display."]
    ) -> str:
        """Muestra una imagen en el Jupyter Notebook."""
        log = IPythonUtils.exec_python(
            f"from IPython.display import Image, display\n\ndisplay(Image(filename='{image_path}'))"
        )
        return "Image displayed successfully" if not log else log


class CodingUtils:
    """Utilidades para la gestión de archivos y código dentro del entorno seguro."""

    @staticmethod
    def list_dir(directory: Annotated[str, "Directory to check."]) -> str:
        """Lista los archivos en el directorio elegido."""
        try:
            safe_dir = _get_safe_path(default_path, directory)
            files = os.listdir(safe_dir)
            return str(files)
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def see_file(filename: Annotated[str, "Name and path of file to check."]) -> str:
        """Comprueba el contenido de un archivo con numeración de líneas."""
        try:
            safe_file_path = _get_safe_path(default_path, filename)
            with open(safe_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
            return "".join(formatted_lines)
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def modify_code(
        filename: Annotated[str, "Name and path of file to change."],
        start_line: Annotated[int, "Start line number to replace."],
        end_line: Annotated[int, "End line number to replace."],
        new_code: Annotated[str, "New code with proper indentation."],
    ) -> str:
        """Reemplaza un bloque de código por uno nuevo."""
        try:
            safe_file_path = _get_safe_path(default_path, filename)
            with open(safe_file_path, "r+", encoding="utf-8") as file:
                file_contents = file.readlines()
                # El slice en Python es exclusivo al final, ajustamos para coincidir con numeración humana
                file_contents[start_line - 1 : end_line] = [new_code + "\n"]
                file.seek(0)
                file.truncate()
                file.write("".join(file_contents))
            return "Code modified successfully"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def create_file_with_code(
        filename: Annotated[str, "Name and path of file to create."],
        code: Annotated[str, "Code to write in the file."],
    ) -> str:
        """Crea un nuevo archivo con el código proporcionado."""
        try:
            safe_file_path = _get_safe_path(default_path, filename)
            directory = safe_file_path.parent
            directory.mkdir(parents=True, exist_ok=True)
            
            with open(safe_file_path, "w", encoding="utf-8") as file:
                file.write(code)
            return "File created successfully"
        except Exception as e:
            return f"Error: {str(e)}"