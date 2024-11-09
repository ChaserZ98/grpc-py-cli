import os
import subprocess
import sys
from platform import machine

import tomllib


def version_info():
    return f"%(prog)s %(version)s (Python {sys.version_info.major}.{sys.version_info.minor} {sys.platform}/{machine()})"


def create_dir_if_not_exists(directory: str) -> None:
    """Create directory if it does not exist

    Args:
        directory (str): Directory path
    """

    if not os.path.exists(directory):
        os.makedirs(directory)


def load_config(config_file: str = "pyproject.toml", root_dir: str = "") -> dict:
    """Load configuration from pyproject.toml file

    Args:
        config_file (str, optional): config file name. Defaults to "pyproject.toml".
        root_dir (str, optional): Root directory of the project. Defaults to "".

    Returns:
        dict: Configuration dictionary
    """

    with open(os.path.join(root_dir, config_file), "rb") as f:
        config = tomllib.load(f)
        config = config.get("tool", {}).get("grpc-py", {})
    return config


def get_default_root_dir() -> str:
    """Get the root directory of the project by searching for pyproject.toml file

    Returns:
        str: Root directory of the project
    """

    current_dir = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current_dir, "pyproject.toml")):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        if current_dir == "/":
            break
    return ""


def generate_grpc_files(
    proto_dir: str,
    proto_filename: str,
    python_out: str,
    grpc_python_out: str,
    pyi_out: str,
):
    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I={proto_dir}",
        f"--python_out={python_out}",
        f"--grpc_python_out={grpc_python_out}",
        f"--pyi_out={pyi_out}",
        proto_filename,
    ]
    res = subprocess.run(command)
    return res.returncode


def ruff_lint(python_out: str, grpc_python_out: str, pyi_out: str):
    command = [
        "ruff",
        "check",
        "--no-cache",
        "--fix",
        python_out,
        grpc_python_out,
        pyi_out,
    ]
    res = subprocess.run(command)
    return res.returncode


def ruff_format(python_out: str, grpc_python_out: str, pyi_out: str):
    command = [
        "ruff",
        "format",
        "--no-cache",
        python_out,
        grpc_python_out,
        pyi_out,
    ]
    res = subprocess.run(command)
    return res.returncode
