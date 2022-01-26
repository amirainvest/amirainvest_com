import os
import subprocess


def update_all_poetry_lock_files():
    project_root = os.path.abspath(__file__).split("bin/update_all_poetry_lock_files.py")[0]
    src_root = os.path.join(project_root, "src")

    subprocess.run("poetry update", shell=True, check=True, cwd=project_root)
    for directory in os.scandir(src_root):
        dir_name = directory.name
        poetry_package_dir = os.path.join(src_root, dir_name)
        subprocess.run("poetry update", shell=True, check=True, cwd=poetry_package_dir)


if __name__ == '__main__':
    update_all_poetry_lock_files()
