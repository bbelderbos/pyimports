import ast
import sys
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Union

import stdlib_list

PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
STANDARD_LIB_MODULES = stdlib_list.stdlib_list(PY_VERSION)
IGNORE_VENV = True


class Module(Enum):
    Stdlib = 1
    External = 2
    Project = 3
    Unknown = 4


def _get_import_nodes(source_code: str) -> list[Union[ast.Import, ast.ImportFrom]]:
    tree = ast.parse(source_code)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]


def get_imports(source_code: str) -> list[str]:
    import_nodes = _get_import_nodes(source_code)

    imported_modules = []
    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imported_modules.append(node.module)

    return list(set(imported_modules))


def get_type_of_module(path: Path, module_name: str) -> Module:
    if module_name in STANDARD_LIB_MODULES:
        return Module.Stdlib
    module_path = module_name.replace(".", "/")
    if (path / f"{module_path}.py").is_file():
        return Module.Project
    else:
        return Module.External
    raise Module.Unknown


def get_modules_by_type(path: Path, imported_modules: list[str]) -> defaultdict[Module, list[str]]:
    modules_by_type = defaultdict(list)
    for module_name in imported_modules:
        origin = get_type_of_module(path, module_name)
        modules_by_type[origin].append(module_name)
    return modules_by_type


if __name__ == "__main__":
    path = Path.cwd()
    files = Path(path).rglob("*.py")
    for file in sorted(files):
        if IGNORE_VENV and "site-packages" in file.parts:
            continue

        source = Path(file).read_text()
        imported_modules = get_imports(source)
        modules_by_type = get_modules_by_type(path, imported_modules)

        print(f"\n{file.relative_to(path)}")
        if len(modules_by_type) == 0:
            print("No imports")
            continue

        for origin, modules in sorted(
            modules_by_type.items(), key=lambda item: item[0].value
        ):
            print(f"{origin.name}: {', '.join(sorted(modules))}")
