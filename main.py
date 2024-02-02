#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
from subprocess import PIPE


def list_desktop_files():
    desktop_files = []
    locations = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        os.path.expanduser("~/.local/share/applications/"),
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


def extract_desktop_entry_info(file_path):
    entry_info_list = []  # List to store multiple entries, including Desktop Actions
    current_entry = None  # Current entry being processed
    current_actions = []  # List to store multiple actions for a single entry
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
                            "file_path": "",
                        }
                        entry_info_list.append(current_entry)
                        continue
                    elif section_name.startswith("Desktop Action "):
                        current_entry = {
                            "name": current_entry["name"] + " ",
                            "comment": "",
                            "generic_name": "",
                            "keywords": "",
                            "exec": "",
                            "nodisplay": False,
                            "file_path": "",
                        }
                        entry_info_list.append(current_entry)
                        continue
                    else:
                        break  # Stop reading once relevant sections are processed
                elif current_entry:
                    if line.startswith("Name="):
                        if current_entry["name"]:
                            current_entry["name"] = (
                                    current_entry["name"]
                                    + "("
                                    + line.split("=", 1)[1]
                                    + ")"
                            )
                        else:
                            current_entry["name"] = line.split("=", 1)[1]

                        print(current_entry["name"])
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
        print(f"Error extracting information from {file_path}: {e}")

    return entry_info_list


def main():
    desktop_files = list_desktop_files()
    entries_info = []  # Modified to store all entries in a single list

    for file in desktop_files:
        entries_info.extend(extract_desktop_entry_info(file))

    # Filter entries without 'NoDisplay' before creating entries_display
    entries_info = [entry for entry in entries_info if not entry["nodisplay"]]

    entries_display = []
    for entry in entries_info:
        if "Desktop Action" in entry["file_path"]:
            # Process entries with [Desktop Action <action name>] section
            action_name = entry["file_path"].split(" ")[-1][:-1]  # Extract action name
            entry_name = f"{entry['name']}({action_name})"
        else:
            # Process regular Desktop Entry section
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

    # Extract the selected application path
    selected_entry = next(
        (
            entry
            for entry in entries_info
            if selected_entry_display.strip()
               == f"{entry['name']}{' - ' + entry['comment'] if entry['comment'] else ''}{' - ' + entry['generic_name'] if entry['generic_name'] else ''}{' - ' + entry['keywords'] if entry['keywords'] else ''}"
        ),
        None,
    )

    if selected_entry:
        if shutil.which("dex"):
            print(selected_entry.get("exec", ""))
            # subprocess.run(
            #     ["dex", selected_entry["file_path"]],
            #     stdout=subprocess.DEVNULL,
            #     stderr=subprocess.DEVNULL,
            # )
        elif shutil.which("gio"):
            print()
            # subprocess.run(
            #     ["gio", "open", selected_entry["file_path"]],
            #     stdout=subprocess.DEVNULL,
            #     stderr=subprocess.DEVNULL,
            # )
        else:
            try:
                exec_command = selected_entry.get("exec", "")
                if exec_command:
                    # subprocess.run(
                    #     f"{exec_command} &",
                    #     shell=True,
                    #     stdout=subprocess.DEVNULL,
                    #     stderr=subprocess.DEVNULL,
                    # )
                    print()
                else:
                    print(f"Error: 'Exec' not found in {selected_entry['file_path']}")
            except Exception as e:
                print(f"Error running application: {e}")


if __name__ == "__main__":
    main()
