import os
import pathlib
import xml.etree.ElementTree as ET


exclude_folders = [
    ".venv",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
]


def fix_python_dirs():
    print("fixing pycharm dirs")
    project_root = os.path.abspath(__file__).split("bin/fix_pycharm_dirs.py")[0]
    src_root = os.path.join(project_root, "src")

    idea_file = pathlib.Path(os.path.join(project_root, ".idea/amirainvest_com.iml"))
    if idea_file.exists() is False:
        raise FileNotFoundError(f"{idea_file} not found")

    tree = ET.parse(idea_file)
    root = tree.getroot()
    for comp in root.findall("component"):
        if comp.get("name") == "NewModuleRootManager":
            component = comp
            break
    else:
        raise KeyError("Could not find component")

    for cont in component.findall("content"):
        if cont.get("url") == "file://$MODULE_DIR$":
            content = cont
            break
    else:
        raise KeyError("could not find content")

    existing_source_folder_urls = set(folder.get("url") for folder in content.findall("sourceFolder"))

    existing_exclude_folders_urls = set(folder.get("url") for folder in content.findall("excludeFolder"))

    for directory in os.scandir(src_root):
        dir_name = directory.name

        for a in ["lib", "test"]:
            url = f"file://$MODULE_DIR$/src/{dir_name}/{a}"

            if url not in existing_source_folder_urls:
                element = ET.Element("sourceFolder")

                element.set("url", url)
                is_test = "false" if a != "test" else "true"
                element.set("isTestSource", is_test)

                content.append(element)

        url = f"file://$MODULE_DIR$/src/{dir_name}/.venv"
        if url not in existing_exclude_folders_urls:
            element = ET.Element("excludeFolder")
            element.set("url", url)
            content.append(element)

    for exclude in exclude_folders:
        url = f"file://$MODULE_DIR$/{exclude}"
        if url not in existing_exclude_folders_urls:
            element = ET.Element("excludeFolder")
            element.set("url", url)
            content.append(element)
    ET.indent(tree)
    tree.write(idea_file, encoding="UTF-8", xml_declaration=True)


if __name__ == '__main__':
    fix_python_dirs()
