import ast
from collections import defaultdict
from enum import Enum
import importlib
from pathlib import Path
import sys

import stdlib_list

PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
STANDARD_LIB_MODULES = stdlib_list.stdlib_list(PY_VERSION)
PROJECT_DIR = Path(__file__).parent
IGNORE_VENV = True


class Module(Enum):
    Stdlib = 1
    External = 2
    Project = 3
    Unknown = 4


def get_imports(source_code: str) -> list[str]:
    tree = ast.parse(source_code)
    import_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    imported_modules = []

    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module)

    # Return a list of unique module names
    return list(set(imported_modules))


def get_type_of_module(module_name: str) -> str:
    if module_name in STANDARD_LIB_MODULES:
        return Module.Stdlib
    module_path = module_name.replace(".", "/")
    if (PROJECT_DIR / f"{module_path}.py").is_file():
        return Module.Project
    else:
        return Module.External
    raise Module.Unknown


def get_modules_by_type(imported_modules: list[str]) -> dict[str, list[str]]:
    modules_by_type = defaultdict(list)
    for module_name in imported_modules:
        origin = get_type_of_module(module_name)
        modules_by_type[origin].append(module_name)
    return modules_by_type


if __name__ == "__main__":
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
    else:
        path = Path.cwd()

    files = Path(path).rglob("*.py")
    for file in files:
        if IGNORE_VENV and "site-packages" in file.parts:
            continue

        source = Path(file).read_text()
        imported_modules = get_imports(source)
        modules_by_type = get_modules_by_type(imported_modules)

        print(f"\n{file.relative_to(PROJECT_DIR)}")
        if len(modules_by_type) == 0:
            print("No imports")
            continue

        for origin, modules in sorted(
            modules_by_type.items(), key=lambda item: item[0].value
        ):
            print(f"{origin.name}: {', '.join(sorted(modules))}")