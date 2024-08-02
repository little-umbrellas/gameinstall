#!/usr/bin/python3

import fnmatch
import os
import sys

def find_file(root_path, file_pattern, file_list):
    for root, _, files in os.walk(root_path):
        for file in files:
            if fnmatch.fnmatch(file.lower(), file_pattern):
                file_list.append(os.path.join(root, file))

def dirtree(path, start, stop=None, step=1):
    dirname = os.path.normpath(path).split(os.sep)[start:stop:step]
    return os.path.join(*['/' if ent == '' else ent for ent in dirname])

def choose_file(path_list, start, stop=None):
    while True:
        count = 0
        print()
        for ent in path_list:
            count += 1
            print(f"[{count}] {dirtree(ent, start, stop)}")

        choice = input(f"Choose one [1..{count}, q (quit)]: ")
        if choice == 'q':
            sys.exit(2)

        try:
            choice = int(choice)
        except:
            print("\nERROR: Invalid input. It must be an integer or the letter q. Try again.", file=sys.stderr)
            continue

        if choice < 1 or choice > count:
            print(f"\nERROR: Input not in range (1..{count}). Try again.", file=sys.stderr)
            continue

        return path_list[choice-1]

HOME = os.getenv("HOME")
assert(HOME)
DOWNLOADSDIR = os.path.join(HOME, "Downloads")
GAMESDIR = os.path.join(HOME, ".wine", "drive_c", "Games")
DESKTOPDIR = os.path.join(HOME, "Desktop")

installable = []
find_file(DOWNLOADSDIR, "setup*.exe", installable)

if not installable:
    print(f"ERROR: No setup file was found in '{DOWNLOADSDIR}'", file=sys.stderr)
    sys.exit(1)

installable.sort(key=os.path.getctime)
mostrecent_installable = dirtree(installable[0], -2, -1)

confirmation = input(f"Install '{mostrecent_installable}'? [y/N] ")
if confirmation.lower() == 'y':
    setup_file = installable[0]
elif len(installable) > 1:
    installable.pop(0)
    setup_file = choose_file(installable, -2, -1)
else:
    print("\nERROR: Unexpected error")
    sys.exit(1)

before_install = os.listdir(GAMESDIR)

winecmd = "wine '" + setup_file + "'"
res = os.system(winecmd)
if res:
    print("\nWARNING: Non-zero return code from wine", file=sys.stderr)

after_install = os.listdir(GAMESDIR)

new_entries = []
for ent in after_install:
    if ent not in before_install:
        new_entries.append(os.path.join(GAMESDIR, ent))

if not new_entries:
    print("\nERROR: Installation unsuccessful", file=sys.stderr)
    sys.exit(1)

executables = []
for ent in new_entries:
    find_file(ent, "*.exe", executables)

if not executables:
    print("\nERROR: No executables were found", file=sys.stderr)
    sys.exit(1)
elif len(executables) > 1:
    print("\nMultiple exe files were found:")
    exe_path = choose_file(executables, -2)
else:
    exe_path = executables[0]

if not exe_path:
    print("\nERROR: Executable not found")
    sys.exit(1)

game_dir = os.path.dirname(exe_path)
game_name = dirtree(game_dir, -1) + ".command"
shortcut_path = os.path.join(DESKTOPDIR, game_name)
exe = dirtree(exe_path, -1)

with open(shortcut_path, 'w') as file:
    file.write("#!/bin/sh\n")
    file.write("cd '" + game_dir + "'\n")
    file.write("wine '" + exe + "'")

os.chmod(shortcut_path, 0o755)
