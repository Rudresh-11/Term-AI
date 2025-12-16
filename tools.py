import subprocess
import os
from typing import List, Dict, Any
from security import validate_path

# --- Tool Implementations ---

def read_file(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        safe_path = validate_path(file_path)
        if not os.path.exists(safe_path):
            return f"Error: File '{file_path}' does not exist."
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Writes content to a file. Overwrites if exists."""
    try:
        safe_path = validate_path(file_path)
        # Note: Actual writing happens after confirmation in the execution layer,
        # but for the tool definition, we assume permission is granted if it reaches here.
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_directory(directory: str = ".") -> str:
    """Lists files and folders in the given directory."""
    try:
        safe_path = validate_path(directory)
        items = os.listdir(safe_path)
        return "\n".join(items) if items else "(Empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def run_shell_command(command: str) -> str:
    """Executes a shell command."""
    # SECURITY: This is handled by the Executor, but the function exists for the LLM schema.
    try:
        # Capture stdout and stderr
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd()
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        return output.strip()
    except Exception as e:
        return f"Error executing command: {str(e)}"

# --- Tool Registry for Gemini ---
# We map function names to the actual callables
TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "run_shell_command": run_shell_command
}

# The tools list passed to the API configuration
TOOLS_SCHEMA = [read_file, write_file, list_directory, run_shell_command]