#!/usr/bin/python3

import fnmatch
import os
import sys

def find_files(file_pattern: str, matches: list[str], path: str = ".") -> None:
    for root, _, files in os.walk(path):
        for file in files:
            if fnmatch.fnmatch(file, file_pattern):
                matches.append(os.path.join(root, file))

def choose_file(files: list[str]) -> str:
    while True:
        idx = 0
        print()
        for file in files:
            idx += 1
            print(f"[{idx}] {file}")
        choice = input(f"Choose file [1..{idx}], [q]uit: ")
        if choice.lower() == 'q' or choice.lower() == "quit":
            sys.exit(2)
        try:
            choice = int(choice)
        except:
            print(f"\nERROR: Input must be an integer or q for quit", file=sys.stderr)
            continue
        if choice < 1 or choice > idx:
            print(f"\nERROR: Choice is out of range", file=sys.stderr)
            continue
        return files[choice-1]

HOME      = os.getenv("HOME")
assert(HOME)

DOWNLOADS = os.path.join(HOME, "Downloads")
GAMES     = os.path.join(HOME, ".wine", "drive_c", "Games")
DESKTOP   = os.path.join(HOME, "Desktop")

assert(os.path.isdir(DOWNLOADS))
assert(os.path.isdir(GAMES))
assert(os.path.isdir(DESKTOP))

os.chdir(DOWNLOADS)

# -- IN DOWNLOADS -- #

setup_files = []
find_files("setup*.exe", setup_files)
if not setup_files:
    print("\nERROR: No setup files were found", file=sys.stderr)
    sys.exit(1)

setup_files.sort(key=os.path.getmtime, reverse=True)
latest_file = setup_files[0]

confirm = input(f"Is '{latest_file}' the game you want to install? [Y/n]: ")
if confirm.lower() == "n":
    setup_files.pop(0)
    setup = choose_file(setup_files)
else:
    setup = setup_files[0]

before_install = os.listdir(GAMES)

ret = os.system("wine '" + setup + "'")
if not ret:
    print("WARNING: Non-zero exit code returned from wine", file=sys.stderr)

after_install  = os.listdir(GAMES)

new_games = [n for n in after_install if n not in before_install]
if not new_games:
    print("ERROR: Installation unsuccessful", file=sys.stderr)
    sys.exit(1)

os.chdir(GAMES)

# -- IN GAMES -- #

exe_files = []
for n in new_games:
    find_files("*.exe", exe_files, n)

if not exe_files:
    print("\nERROR: No exe files were found", file=sys.stderr)
    sys.exit(1)

if len(exe_files) > 1:
    exe = choose_file(exe_files)
else:
    exe = exe_files[0]

parts    = os.path.normpath(exe).split('/')
name     = parts[0]
exe      = os.path.join(*parts[1:])
path     = os.path.join(GAMES, name)
shortcut = os.path.join(DESKTOP, (name + ".command"))

if os.path.isfile(shortcut):
    confirm = input(f"\nOverwrite existing file '{shortcut}'? [y/N]: ")
    if confirm.lower() != 'y' and confirm.lower() != "yes":
        sys.exit()
    os.remove(shortcut)

fd = os.open(shortcut, os.O_WRONLY|os.O_CREAT, mode=0o755)
with open(fd, 'w') as f:
    f.write("#!/bin/sh\n")
    f.write(f"cd '{path}'\n")
    f.write(f"wine '{exe}'\n")
