import subprocess
from typing import List

def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command safely."""
    try:
        result = subprocess.run(command, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {' '.join(command)}\nError: {e.stderr}"
        raise RuntimeError(error_msg) from e
