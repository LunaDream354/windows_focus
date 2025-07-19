import ast
import subprocess
import sys
import importlib.util
import os

def get_imports_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filename)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def is_installed(module_name):
    return importlib.util.find_spec(module_name) is not None

def install_package(package):
    try:
        print(f"Installing: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"Failed to install: {package}")

def install_dependencies(script_path):
    if not os.path.isfile(script_path):
        print(f"File not found: {script_path}")
        return

    print(f"Checking imports in: {script_path}\n")
    imported_modules = get_imports_from_file(script_path)
    missing_modules = [m for m in imported_modules if not is_installed(m)]

    if not missing_modules:
        print("All dependencies are already installed.")
    else:
        print("Missing modules found:", ", ".join(missing_modules))
        for module in missing_modules:
            install_package(module)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python auto_install_deps.py your_script.py")
    else:
        script_to_check = sys.argv[1]
        install_dependencies(script_to_check)
