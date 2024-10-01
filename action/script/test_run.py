import json
import importlib
import os


def main():
    parsed_args = {}
    for env_var_name, env_var_type in (
        ("pyargs", list),
        ("args", list),
        ("overrides", dict),
    ):
        env_var_value = os.environ.get(f"RD_PYTESTER__{env_var_name.upper()}")
        if not env_var_value:
            parsed_args[env_var_name] = None
            continue
        try:
            env_var_value = json.loads(env_var_value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse '{env_var_name}' environment variable as JSON.") from e
        if not isinstance(env_var_value, env_var_type):
            raise ValueError(f"Expected '{env_var_name}' environment variable to be of type '{env_var_type}'.")
        parsed_args[env_var_name] = env_var_value
    tests_name = os.environ.get("RD_PYTESTER__TESTS_NAME")
    if not tests_name:
        raise ValueError("Environment variable 'RD_PYTESTER__TESTS_NAME' is not set.")
    tester = importlib.import_module(tests_name)
    tester.run(
        **parsed_args,
        path_cache="cache",
        path_report="report",
    )
    return


if __name__ == "__main__":
    main()
