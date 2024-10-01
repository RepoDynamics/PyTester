from typing import Callable, Literal, get_type_hints
import sys
import os
from pathlib import Path
import time

import actionman
import pyshellman
from loggerman import logger

from pytester import ENV_PREFIX
from pytester.logger import initialize_logger


def venv_executable_path(venv_path: Path, executable_name: str) -> Path:
    if os.name == "nt":
        dir_name = "Scripts"
        suffix = ".exe"
    else:
        dir_name = "bin"
        suffix = ""
    return venv_path / dir_name / f"{executable_name}{suffix}"


class EnvSetup:

    def __init__(
        self,
        python_path: str | Path,
        repo_path: str | Path,
    ):
        venv_path = Path(".venv")
        pyshellman.run(
            command=[str(python_path), "-m", "venv", str(venv_path), "--upgrade-deps"],
            logger=logger,
            log_title="Virtual Environment Setup",
        )
        venv_python_path = venv_executable_path(venv_path, "python")
        actionman.env_var.write(f"{ENV_PREFIX}VENV_PYTHON_PATH", str(venv_python_path))
        self._pip_runner = pyshellman.Runner(
            pre_command=[str(venv_python_path), "-m", "pip"],
            logger=logger,
        )
        self._repo_path = Path(repo_path)
        return

    def install_package(
        self,
        src: Literal["github", "testpypi", "pypi"],
        path: str | None = None,
        name: str | None = None,
        version: str | None = None,
        req_path: str | None = None,
        retries: int = 40,
        retry_sleep_seconds: float = 15,
    ):
        if req_path:
            self._install_pkg_requirements(path=req_path)
        if src == "github":
            return self._install_from_github(
                path=path,
                log_title="Package Installation (GitHub)",
            )
        return self._install_from_pypi(
            src=src,
            name=name,
            version=version,
            retries=retries,
            retry_sleep_seconds=retry_sleep_seconds,
        )

    def install_testsuite(self, path: str):
        return self._install_from_github(
            path=path,
            log_title="Test-Suite Installation (GitHub)",
        )

    def display_env(self):
        self._pip_runner.run(
            command=["list"],
            log_title="Environment Overview",
        )

    def _install_from_github(self, path: str, log_title: str):
        fullpath = self._repo_path / path
        self._pip_runner.run(
            command=["install", str(fullpath)],
            log_title=log_title,
        )
        return

    def _install_pkg_requirements(self, path: str):
        fullpath = self._repo_path / path
        self._pip_runner.run(
            command=["install", "-r", str(fullpath)],
            log_title="Package Requirements Installation",
        )
        return

    def _install_from_pypi(
        self,
        src: Literal["testpypi", "pypi"],
        name: str,
        version: str | None = None,
        retries: int = 40,
        retry_sleep_seconds: float = 15,
    ):
        command = ["install", name if not version else f"{name}=={version}"]
        if src == "testpypi":
            command.extend(["--no-deps", "--index-url", "https://test.pypi.org/simple"])
            src_name = "TestPyPI"
        else:
            src_name = "PyPI"
        for retry_count in range(retries):
            result = self._pip_runner.run(
                command=command,
                log_title=f"Package Installation ({src_name}, attempt {retry_count + 1})",
                raise_exit_code=False,
                log_level_exit_code="info",
            )
            if result.succeeded:
                break
            time.sleep(retry_sleep_seconds)
        else:
            logger.critical(
                f"Package Installation ({src_name})",
                f"Failed to install package from {src_name} after {retries} attempts "
                f"with a total sleep time of {retries * retry_sleep_seconds} seconds.",
            )
            sys.exit(1)
        return


def main():
    initialize_logger([1, 3, 2])
    logger.section("Package & Test-Suite")
    init_args = {
        name.lower(): actionman.env_var.read(f"{ENV_PREFIX}{name}", str)
        for name in ("PYTHON_PATH", "REPO_PATH")
    }
    pkg_args = {
        name.removeprefix("PKG_").lower(): actionman.env_var.read(f"{ENV_PREFIX}{name}", str)
        for name in ("PKG_SRC", "PKG_PATH", "PKG_NAME", "PKG_VERSION", "PKG_REQ_PATH")
    }
    pkg_src = pkg_args["src"].lower()
    if pkg_src not in ("github", "pypi", "testpypi"):
        sys.exit(
            f"Invalid input for 'pkg-src': "
            f"Expected one of 'GitHub', 'PyPI', or 'TestPyPI', but got '{pkg_src}'."
        )
    setup_environment = EnvSetup(**init_args)
    setup_environment.install_package(
        retries=actionman.env_var.read(f"{ENV_PREFIX}RETRIES", int),
        retry_sleep_seconds=actionman.env_var.read(f"{ENV_PREFIX}RETRY_SLEEP_SECONDS", int),
        **pkg_args
    )
    setup_environment.install_testsuite(
        path=actionman.env_var.read(f"{ENV_PREFIX}TESTS_PATH", str),
    )
    setup_environment.display_env()
    return


if __name__ == "__main__":
    main()