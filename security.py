import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def get_cwd():
    return Path.cwd()

def validate_path(file_path: str) -> str:
    """
    Sandboxing: Ensures the path is within the current working directory.
    Resolves relative paths and checks against CWD.
    """
    cwd = get_cwd()
    # Resolve the absolute path
    target = (cwd / file_path).resolve()
    
    # Check if target starts with CWD (prevents traversal like ../../etc/passwd)
    if not str(target).startswith(str(cwd)):
        raise PermissionError(f"Access denied: Path '{file_path}' is outside the current working directory.")
    
    return str(target)

def confirm_action(action_type: str, details: str) -> bool:
    """
    Gating: Forces user confirmation for sensitive actions.
    """
    console.print(f"\n[bold yellow]⚠️  CONFIRMATION REQUIRED[/bold yellow]")
    console.print(f"[bold]{action_type}:[/bold] {details}")
    return Confirm.ask("Do you want to proceed?", default=False)