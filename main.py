#!/usr/bin/env python3
"""
Program Name: clilauncher (nokludge)
Description: A Python script for launching desktop applications with fuzzy search and action support.
Author: Elvin deSouza
Copyright (c) 2024 Elvin deSouza
License: GPL License (see LICENSE file for details)
"""

import logging
import os
import re
import subprocess
from subprocess import PIPE

logging.basicConfig(
    level=logging.INFO,  # INFO, DEBUG, WARNING, ERROR
    format="%(levelname)s: %(message)s",
)


def list_desktop_files() -> list[str]:
    """
    Description: Retrieves a list of desktop files from standard locations.
    Returns: List of file paths for desktop entries.
    """
    desktop_files = []
    # you can add custom locations for .desktop files to the end
    locations = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        os.path.expanduser("~/.local/share/applications/"),
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
        "/var/lib/snapd/desktop/applications/",
        os.path.expanduser("~/snap/*/current/.local/share/applications/"),
        "/var/lib/flatpak/exports/share/applications/",
        "/media/elvin/extra/Flatpak/flatpak/exports/share/applications/",
        "/media/elvin/dHDD/Flatpak/flatpak/exports/share/applications/",
    ]

    for location in locations:
        if os.path.exists(location):
            desktop_files.extend(
                [
                    os.path.join(location, file)
                    for file in os.listdir(location)
                    if file.endswith(".desktop")
                ]
            )

    return desktop_files


def extract_desktop_entry_info(file_path: str):
    """
    Description: Extracts information from a desktop entry file.
    Parameters:  file_path (str): Path to the desktop entry file.
    Returns: List of dictionaries containing entry details.
    """
    entry_info_list = []  # List to store multiple entries, including Desktop Actions
    current_entry = None  # Current entry being processed
    try:
        with open(file_path, "r") as desktop_file:
            for line in desktop_file:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    section_name = line[1:-1]
                    if section_name == "Desktop Entry":
                        current_entry = {
                            "name": "",
                            "comment": "",
                            "generic_name": "",
                            "keywords": "",
                            "exec": "",
                            "nodisplay": False,
                            "file_path": file_path,
                            "is_action": False,
                        }
                        entry_info_list.append(current_entry)
                        application_name = ""  # Reset application name for each entry
                        continue
                    elif section_name.startswith("Desktop Action "):
                        current_entry = {
                            "name": application_name + " ",
                            "comment": "",
                            "generic_name": "",
                            "keywords": "",
                            "exec": "",
                            "nodisplay": False,
                            "file_path": file_path,
                            "is_action": True,
                        }
                        entry_info_list.append(current_entry)
                        continue
                    else:
                        break
                elif current_entry:
                    if line.startswith("Name="):
                        if current_entry["name"]:
                            current_entry[
                                "name"
                            ] = f"{current_entry['name']} ({line.split('=', 1)[1]})"
                        else:
                            current_entry["name"] = line.split("=", 1)[1]

                        if not current_entry["is_action"]:
                            application_name = current_entry["name"]
                    elif line.startswith("Comment="):
                        current_entry["comment"] = line.split("=", 1)[1]
                    elif line.startswith("GenericName="):
                        current_entry["generic_name"] = line.split("=", 1)[1]
                    elif line.startswith("Keywords="):
                        current_entry["keywords"] = line.split("=", 1)[1]
                    elif line.startswith("Exec="):
                        current_entry["exec"] = re.sub(r"%.", "", line.split("=", 1)[1])
                    elif line.startswith("NoDisplay=true"):
                        current_entry["nodisplay"] = True

    except Exception as e:
        logging.error(f"Error extracting information from {file_path}: {e}")

    return entry_info_list


def main():
    desktop_files = list_desktop_files()
    entries_info = []

    for file in desktop_files:
        entries_info.extend(extract_desktop_entry_info(file))

    # Entries without 'NoDisplay' are not shown in menu
    entries_info = [entry for entry in entries_info if not entry["nodisplay"]]

    entries_display = []
    for entry in entries_info:
        if "Desktop Action" in entry["file_path"]:
            # [Desktop Action <action name>]
            action_name = entry["file_path"].split(" ")[-1][:-1]
            entry_name = f"{entry['name']}({action_name})"
        else:
            entry_name = entry["name"]

        entries_display.append(
            f"{entry_name}{' - ' + entry['comment'] if entry['comment'] else ''}{' - ' + entry['generic_name'] if entry['generic_name'] else ''}{' - ' + entry['keywords'] if entry['keywords'] else ''}"
        )

    # Use fzf for searching and selection
    with subprocess.Popen(
            ["fzf"], stdin=PIPE, stdout=PIPE, universal_newlines=True
    ) as fzf_process:
        fzf_input = "\n".join(entries_display)
        selected_entry_display, _ = fzf_process.communicate(input=fzf_input)

    selected_entry = next(
        (
            entry
            for entry in entries_info
            if selected_entry_display.strip()
               == f"{entry['name']}{' - ' + entry['comment'] if entry['comment'] else ''}{' - ' + entry['generic_name'] if entry['generic_name'] else ''}{' - ' + entry['keywords'] if entry['keywords'] else ''}"
        ),
        None,
    )

    if not selected_entry:
        return
    try:
        exec_command = selected_entry.get("exec", "")
        if exec_command:
            subprocess.run(
                f"{exec_command} &",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            logging.error(f"Error: 'Exec' not found in {selected_entry['file_path']}")
    except Exception as e:
        logging.error(f"Error running application: {e}")


if __name__ == "__main__":
    main()
