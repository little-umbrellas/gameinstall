#!/usr/bin/python3

from pathlib import Path
import fnmatch
import os
import sys

def find_file(file_pattern: str, matches: list[str], root_path=".") -> bool:
    foundFile = False
    for root, _, files in os.walk(root_path):
        for file in files:
            if fnmatch.fnmatch(file, file_pattern):
                if not foundFile:
                    foundFile = True
                matches.append(os.path.join(root, file))
    return foundFile

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

HOME = os.getenv("HOME")
assert(HOME)

DOWNLOADS = os.path.join(HOME, "Downloads")
GAMES     = os.path.join(HOME, ".wine", "drive_c", "Games")
DESKTOP   = os.path.join(HOME, "Desktop")
assert(os.path.exists(DOWNLOADS))
assert(os.path.exists(GAMES))
assert(os.path.exists(DESKTOP))

os.chdir(DOWNLOADS)

setup_files = []
if not find_file("setup*.exe", setup_files):
    print("\nERROR: No setup files were found", file=sys.stderr)
    sys.exit(1)

setup_files.sort(key=os.path.getmtime, reverse=True)
confirm = input(f"Is '{setup_files[0]}' the game you want to install? [Y/n]: ")

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

exe_files = []
for n in new_games:
    if os.path.isdir(n):
        find_file("*.exe", exe_files, n)

if not exe_files:
    print("\nERROR: No exe files were found", file=sys.stderr)
    sys.exit(1)

if len(exe_files) > 1:
    exe = choose_file(exe_files)
else:
    exe = exe_files[0]

game_name     = str(Path(exe).parent)
game_path     = os.path.join(GAMES, game_name)
launcher_file = os.path.join(DESKTOP, game_name + ".command")

fd = os.open(launcher_file, os.O_WRONLY|os.O_CREAT, mode=0o755)
with open(fd, 'w') as f:
    f.write("#!/bin/sh\n")
    f.write("cd '" + game_path + "'\n")
    f.write("wine '" + exe.replace(game_name + os.sep, "") + "'")
