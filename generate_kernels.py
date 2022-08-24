from functools import partial
import json
from pathlib import Path
import subprocess
from typing import Any, Callable, Dict, List, Optional, Union

import yaml


def create_conda_environment(environment_name: str, python_version: str):
    """
    Creates a conda environment with the specified name and Python version
    """
    command = f"conda create -y -n {environment_name} python={python_version} ipykernel"
    run_and_echo(command)


def create_kernel_json(
    environment_name: str,
    display_name: str,
    save_path: Optional[Union[str, Path]],
    static_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Creates a kernel JSON object
    """
    kernel_json = {
        "argv": [
            get_python_executable(environment_name),
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ],
        "display_name": display_name,
        "language": "python",
    }
    if save_path:
        if not isinstance(save_path, Path):
            save_path = Path(save_path)
        # Create save_path/environment_name if it doesn't exist
        (save_path / environment_name).mkdir(parents=True, exist_ok=True)
        # Copy everything from static_path to save_path/environment_name
        if static_path:
            for f in list_files_in_directory(static_path):
                run_and_echo(f"cp {f} {save_path / environment_name}")
        # Write kernel.json to save_path/environment_name
        with open(save_path / environment_name / "kernel.json", "w") as f:
            json.dump(kernel_json, f, indent=4)
    return kernel_json


def get_python_executable(conda_environment_name: str) -> str:
    """
    Returns the path to the Python executable in a conda environment
    """
    return run_and_get_output(
        f'conda run -n {conda_environment_name} python -c "import sys; print(sys.executable)"'
    )


def install_dependencies_with_pip(
    conda_environment_name: str, dependencies: List[str]
) -> None:
    """
    Installs dependencies with pip
    """
    python_executable = get_python_executable(conda_environment_name)
    run_and_echo(f"{python_executable} -m pip install {' '.join(dependencies)}")


def install_dependencies_with_poetry(
    conda_environment_name: str, dependencies: List[str]
) -> None:
    """
    Installs dependencies with poetry
    """
    python_executable = get_python_executable(conda_environment_name)
    run_and_echo(f"{python_executable} -m pip install poetry")
    run_and_echo(f"mkdir -p /tmp/{conda_environment_name}")
    run_and_echo(
        f"cd /tmp/{conda_environment_name} && {python_executable} -m poetry init -n"
    )
    run_and_echo(
        f"cd /tmp/{conda_environment_name} && {python_executable} -m poetry add -n {' '.join(dependencies)}"
    )
    run_and_echo(
        f"cd /tmp/{conda_environment_name} && {python_executable} -m poetry install -n"
    )


def install_kernel(
    environment_name: str, display_name: str,
):
    """
    Installs a kernel
    """
    log(f"Installing kernel: {display_name}")
    python_executable = get_python_executable(environment_name)
    run_and_echo(
        f'{python_executable} -m ipykernel install --user --name="{environment_name}"'
    )


def list_files_in_directory(directory: Union[str, Path], extension: str = None):
    """
    Lists all files in a directory, optionally filtering by extension
    """
    if not isinstance(directory, Path):
        directory = Path(directory)
    if extension:
        return [f for f in directory.iterdir() if f.suffix == extension]
    return [f for f in directory.iterdir()]


def load_yaml_file(path: Union[str, Path]) -> Any:
    """
    Loads a YAML file and returns the contents
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)


def log(
    message: Any, level: str = "info",
):
    """
    Logs a message to stdout. Format is:
    [<level-4-char>] <message>
    """
    allowed_levels = ["info", "warning", "error"]
    if level not in allowed_levels:
        raise ValueError(f"Invalid level: {level}")
    print(f"[{level.upper():<4}] {message}")


def run_and_echo(
    command: str,
    stdout_callback: Callable = partial(print, end=""),
    on_error: Union[Callable, str] = "raise",
) -> int:
    """
    Echoes the command and then runs it, sending output to stdout_callback
    """
    allowed_on_errors = ["raise", "return"]
    if on_error not in allowed_on_errors and not callable(on_error):
        log(f"Invalid on_error value: {on_error}", "error")
        raise ValueError(f"Invalid on_error: {on_error}")
    log(command)
    popen = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, universal_newlines=True
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        stdout_callback(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        if callable(on_error):
            on_error(return_code)
        elif on_error == "raise":
            log(f"{command} failed with exit code {return_code}", "error")
            exit(return_code)
        else:
            return return_code
    return return_code


def run_and_get_output(command: str):
    """
    Runs a command and returns the output
    """
    return subprocess.check_output(command, shell=True).decode().strip()


if __name__ == "__main__":

    # List all YAML files in the `kernels/` directory
    log("Listing YAML files in kernels/")
    kernel_files = list_files_in_directory("kernels", ".yaml")
    log(f"Found {len(kernel_files)} YAML files")

    # Load each YAML file and create a conda environment for each
    for kernel_file in kernel_files:
        log(f"Loading {kernel_file}")
        kernel = load_yaml_file(kernel_file)

        kernel_name = Path(kernel_file).stem
        kernel_display_name = kernel["metadata"]["display_name"]
        kernel_python_version = kernel["metadata"]["python_version"]
        kernel_use_poetry = kernel["metadata"]["use_poetry"]

        log(f"Creating conda environment {kernel_name}")
        create_conda_environment(kernel_name, kernel_python_version)

        if kernel_use_poetry:
            log(f"Installing dependencies with poetry")
            install_dependencies_with_poetry(kernel_name, kernel["dependencies"])
        else:
            log(f"Installing dependencies with pip")
            install_dependencies_with_pip(kernel_name, kernel["dependencies"])

        log(f"Creating kernel.json for {kernel_name}")
        create_kernel_json(
            kernel_name,
            kernel_display_name,
            save_path="/opt/conda/share/jupyter/kernels/",
            static_path="/tmp/_static",
        )
