# document_processor.py
# This file reads markdown files from a folder.

from pathlib import Path


def read_markdown_folder(folder_path):
    """
    This function reads all .md files inside one folder.

    A function is a reusable block of code.
    folder_path is the location of the folder we want to read.
    """

    folder = Path(folder_path)
    all_text = ""

    # This checks if the folder exists.
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    # This loops through every markdown file in the folder.
    for file in folder.glob("*.md"):
        content = file.read_text(encoding="utf-8")
        all_text += f"\n\n--- {file.name} ---\n"
        all_text += content

    return all_text
