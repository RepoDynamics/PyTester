from typing import Callable, Literal
import sys
import traceback
from pathlib import Path

import actionman
import retryit
import pyshellman
from loggerman import logger


def setup_environment(
    path_repo: str,
    path_setup_testsuite: str,
    path_setup_package: str,
    package_source: str,
    package_name: str,
    package_version: str,
    path_requirements_package: str,
    retry_sleep_seconds: float,
    retry_sleep_seconds_total: float,
):
    logger.section("Installation")
    source = package_source.lower()
    if source not in ("github", "pypi", "testpypi"):
        sys.exit(
            f"Invalid input for 'package-source': "
            f"Expected one of 'GitHub', 'PyPI', or 'TestPyPI', but got '{source}'."
        )
    path_repo = Path(path_repo).resolve()
    install_package(
        source=source,
        path_repo=path_repo,
        path_setup_package=path_setup_package,
        path_requirements_package=path_requirements_package,
        package_name=package_name,
        package_version=package_version,
        retry_sleep_seconds=retry_sleep_seconds,
        retry_sleep_seconds_total=retry_sleep_seconds_total,
    )
    install_testsuite(
        path_repo=path_repo,
        path_setup_testsuite=path_setup_testsuite,
    )
    logger.section_end()
    return


def install_package(
    source: Literal["github", "testpypi", "pypi"],
    path_repo: Path,
    path_setup_package: str,
    path_requirements_package: str,
    package_name: str,
    package_version: str,
    retry_sleep_seconds: float,
    retry_sleep_seconds_total: float,
):

    def get_retry_func() -> Callable:
        def return_handler(shell_output: pyshellman.ShellOutput):
            return not shell_output.succeeded
        retry_logger = retryit.logger.full(
            log_function=logger.entry,
            title=(
                f"Install Package From {'TestPyPI' if source == 'testpypi' else 'PyPI'} "
                f"(attempt {{count_tries}})"
            ),
            details=(
                "Command: {value.cmd}",
                "Executed: {value.executed}",
                "Exit Code: {value.code}",
                "Output: {value.out}",
                "Error: {value.err}",
            ),
            case_return_accepted=(
                "pass",
                (
                    f"Installing package from {'TestPyPI' if source == 'testpypi' else 'PyPI'} "
                    f"was successful. {{value.summary}}"
                )
            ),
            case_return_rejected_and_retry=(
                "attention",
                f"Installing package from {'TestPyPI' if source == 'testpypi' else 'PyPI'} failed. "
                f"{{value.summary}} Installation will be retried in {{next_sleep_seconds}} seconds."
            ),
            case_return_rejected_and_timeout=(
                "fail",
                f"Installing package from {'TestPyPI' if source == 'testpypi' else 'PyPI'} failed. "
                f"{{value.summary}} The retry limit has been reached; action will fail."
            )
        )
        return retryit.retry(
            pyshellman.pip.install_package,
            sleeper=retryit.sleeper.constant_until_max_duration(
                sleep_seconds=retry_sleep_seconds, total_seconds=retry_sleep_seconds_total
            ),
            exception_handler=None,
            return_handler=return_handler,
            logger=retry_logger,
        )

    if source == "github":
        submit_log_shell_output(
            shell_output=pyshellman.pip.install(
                command=[path_setup_package],
                cwd=path_repo,
            ),
            title="Install Package From GitHub",
            prepend_summary="Installing package from GitHub",
        )
        return
    elif source == "testpypi":
        path_requirements = (path_repo / path_requirements_package).resolve()
        if path_requirements.is_file():
            submit_log_shell_output(
                shell_output=pyshellman.pip.install_requirements(
                    path=path_requirements_package,
                    cwd=path_repo,
                ),
                title="Install Package Requirements",
                prepend_summary="Installing package requirements",
            )
        else:
            logger.entry(
                status="skip",
                title="Install Package Requirements",
                summary="No requirements file found.",
                details=[
                    f"Input Path: {path_requirements_package}",
                    f"Resolved Path: {path_requirements}",
                ],
            )
        try:
            get_retry_func()(
                name=package_name,
                requirement_specifier=f"=={package_version}" if package_version else None,
                install_dependencies=False,
                index="testpypi",
            )
        except retryit.exception.RetryError as e:
            sys.exit(
                f"Installing package from TestPyPI failed "
                f"after {e.count_tries} tries totaling {e.total_sleep_seconds} seconds."
            )
    else:
        try:
            get_retry_func()(
                name=package_name,
                requirement_specifier=f"=={package_version}" if package_version else None,
            )
        except retryit.exception.RetryError as e:
            sys.exit(
                f"Installing package from PyPI failed "
                f"after {e.count_tries} tries totaling {e.total_sleep_seconds} seconds."
            )
    return


def install_testsuite(
    path_repo: Path,
    path_setup_testsuite: str,
):
    submit_log_shell_output(
        shell_output=pyshellman.pip.install(
            command=[path_setup_testsuite],
            cwd=path_repo,
        ),
        title="Install Test-Suite",
        prepend_summary="Installing test-suite",
    )
    return


def submit_log_shell_output(
    shell_output: pyshellman.ShellOutput,
    title: str,
    prepend_summary: str = "",
):
    pre_summary = (
        f"{prepend_summary} {'was successful' if shell_output.succeeded else 'failed'}. "
        if prepend_summary else ""
    )
    summary = f"{pre_summary}{shell_output.summary}"
    logger.entry(
        status="pass" if shell_output.succeeded else "fail",
        title=title,
        summary=summary,
        details=shell_output.details,
    )
    if not shell_output.succeeded:
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdin.flush()
        sys.exit(summary)
    return


if __name__ == "__main__":
    try:
        # logger = actionman.log.logger(initial_section_level=3)
        logger.initialize(
            init_section_number=3,
            github=True,
        )
        logger.section("Package & Test-Suite Setup")
        inputs = actionman.io.read_function_args_from_environment_variables(
            function=setup_environment,
            name_prefix="RD_PYTESTER_ES__",
            logger=logger,
        )
        setup_environment(**inputs)
        logger.section_end()
        logger.section("Environment Info")
        logger.entry(
            status="info",
            title="Python Version",
            details=[f"Python version: {sys.version}"],
        )
        logger.entry(
            status="info",
            title="Installed Packages",
            summary=pyshellman.pip.list().output,
        )
        logger.entry(
            status="info",
            title="Hardware and OS Info",
            summary=pyshellman.run(["uname", "-a"]).output,
        )
        logger.entry(
            status="info",
            title="System Resources",
            summary=pyshellman.run(["ulimit", "-a"]).output,
        )
        logger.entry(
            status="info",
            title="Disk Space",
            summary=pyshellman.run(["df", "-h"]).output,
        )
    except Exception as e:
        sys.stdout.flush()
        sys.exit(f"{e.__class__.__name__}: {e}\n{traceback.format_exc()}")
