#!/usr/bin/env python3
import os
import subprocess
import shutil
import re
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
    entry_info = {
        "name": "",
        "comment": "",
        "generic_name": "",
        "keywords": "",
        "exec": "",  # New entry for storing the exec command
        "nodisplay": False,
        "file_path": "",
    }
    current_section = ""  # Default section
    try:
        with open(file_path, "r") as desktop_file:
            entry_info["file_path"] = file_path
            for line in desktop_file:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]  # Extract section name
                    if current_section == "Desktop Entry":
                        continue  # Continue to read only from [Desktop Entry] section
                    else:
                        break  # Stop reading once [Desktop Entry] section is over
                elif current_section == "Desktop Entry":
                    if line.startswith("Name="):
                        entry_info["name"] = line.split("=", 1)[1]
                    elif line.startswith("Comment="):
                        entry_info["comment"] = line.split("=", 1)[1]
                    elif line.startswith("GenericName="):
                        entry_info["generic_name"] = line.split("=", 1)[1]
                    elif line.startswith("Keywords="):
                        entry_info["keywords"] = line.split("=", 1)[1]
                    elif line.startswith("Exec="):
                        entry_info["exec"] = re.sub(r'%.', '', line.split("=", 1)[1])
                    elif line.startswith("NoDisplay=true"):
                        entry_info["nodisplay"] = True

    except Exception as e:
        print(f"Error extracting information from {file_path}: {e}")

    return entry_info


def main():
    desktop_files = list_desktop_files()
    entries_info = [extract_desktop_entry_info(file) for file in desktop_files if not extract_desktop_entry_info(file)['nodisplay']]

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
    with subprocess.Popen(['fzf'], stdin=PIPE, stdout=PIPE, universal_newlines=True) as fzf_process:
        fzf_input = '\n'.join(entries_display)
        selected_entry_display, _ = fzf_process.communicate(input=fzf_input)

    # Extract the selected application path
    selected_entry = next((entry for entry in entries_info if selected_entry_display.strip() == f"{entry['name']}{' - ' + entry['comment'] if entry['comment'] else ''}{' - ' + entry['generic_name'] if entry['generic_name'] else ''}{' - ' + entry['keywords'] if entry['keywords'] else ''}"), None)

    if selected_entry:
        if shutil.which("dex"):
            subprocess.run(['dex', selected_entry['file_path']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif shutil.which("gio"):
            subprocess.run(['gio', 'open', selected_entry['file_path']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            try:
                exec_command = selected_entry.get("exec", "")
                if exec_command:
                    subprocess.run(f'{exec_command} &', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    print(f"Error: 'Exec' not found in {selected_entry['file_path']}")
            except Exception as e:
                print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
