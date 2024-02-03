# clilauncher (nokludge)

## Description

I was wondering why there is no popular and supported CLI application launcher(non-CLI ones would be dmenu, krunner, rofi, etc.), so I decided to write one myself.

It needed to have a filter-as-you-type search, Ctrl+j and Ctrl+k navigation in the list, and when running an application it should not hold the terminal captive(foreground) and not dump console output to the terminal.

`clilauncher` is a Python script for launching desktop applications with fuzzy search and action support. It provides a convenient and efficient way to find and execute applications from the command line.

## Features
- Fuzzy search for desktop applications.
- Support for desktop actions(like opening a private tab in a browser)
- Works with installed Snap and Flatpaks too, if not using custom directories
- Lightweight and easy to use.

## Prerequisites
- Python 3.x
- FZF (Fuzzy Finder) - using your package manager (`sudo apt-get install fzf`, `brew install fzf`, etc.), or from https://github.com/junegunn/fzf

## Optional Dependencies
Does not depend on gio or dex, use the version on `master` if needed

## Usage
1. Run `main.py`
2. Use fzf to search and select the desired application.
3. Launch the selected application or action.

## Setup
1. Clone the repository
2. Rename the script and move it to a directory on $PATH
3. Make the script executable: `chmod +x main.py`
4. Run the script: `./main.py`

## Known Issues
- Experimental method for launching applications without `dex` or `gio` fetches the Exec line from the .desktop file and omits the substitution variables, it is possible that it fails to launch an application correctly. It is very unlikely, though.

## Author
- Elvin deSouza

## License
This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.
