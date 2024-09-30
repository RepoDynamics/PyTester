import os
import json
import sys
from pathlib import Path
import subprocess


def shell_command(command):
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
    )

def pip_install(command):
    return shell_command(["python", "-m", "pip", "install", *command])


def read_env_var(name, typ):
    value = os.environ.get(name)
    if value is None:
        return
    if typ is str:
        return value
    value = json.loads(value)
    if not isinstance(value, typ):
        raise ValueError(f"Environment variable '{name}' is not of type '{typ}'")
    return value

def install_pkg_from_github(path: Path):
    output = pip_install([str(path)])
    return


if __name__ == "__main__":
    env_prefix = "RD_PYTESTER__"
    repo_path = Path(read_env_var(f"{env_prefix}REPO_PATH", str))
    pkg_src = read_env_var(f"{env_prefix}PKG_SRC", str).lower()
    if pkg_src not in ("github", "pypi", "testpypi"):
        sys.exit(
            f"Invalid input for 'pkg-src': "
            f"Expected one of 'GitHub', 'PyPI', or 'TestPyPI', but got '{pkg_src}'."
        )
    if pkg_src == "github":
        install_pkg_from_github(
            pkg_name=read_env_var(f"{env_prefix}PKG_NAME", str),
            pkg_version=read_env_var(f"{env_prefix}PKG_VERSION", str),
            path_repo=repo_path,
            path_setup=read_env_var(f"{env_prefix}PKG_SETUP", str),
        )
