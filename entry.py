#!/usr/bin/env python3
import os
import sys
import subprocess
import venv
import shutil

DIR = os.path.dirname(__file__)
VENV_DIR = os.path.abspath(os.path.join(DIR, ".venv"))
EXEC_DIR = "Scripts" if os.name == "nt" else "bin"
MAIN = os.path.join(DIR, "src", "main.py")
VENV_PYT = os.path.join(VENV_DIR, EXEC_DIR, "python3")

def detect(command,package):
    if shutil.which(command):
        print(f'{package} found ✅')
    else:
        print(f'{package} not found ❌.')

def bootstraping():
    print("[BOOTSTRAPING INITIATED]")
    if sys.prefix == sys.base_prefix:
        if os.path.exists(VENV_DIR):
            print(f"Found Virtual Environment ...")
            if input("Reinstall? [y/N] "):
                shutil.rmtree(VENV_DIR)
                venv.create(VENV_DIR, with_pip=True)
        else:
            print(f"Creating a Virtual Environment @ {VENV_DIR} ...")
            venv.create(VENV_DIR, with_pip=True)
        pip = os.path.join(VENV_DIR, EXEC_DIR, "pip")
        subprocess.check_call([pip, "install", "--upgrade", "pip"])
        os.chdir(DIR)
        subprocess.check_call([VENV_PYT, "-m", "pip", "install", "-e", "."])
        subprocess.check_call([pip, "install", "-e", DIR])
    else:
        print("Already in an Vitual Environment")
        print("RUN `deactivate`")
    detect("fzf","fzf")
    detect("termux-info","termux-api")
    print("[BOOTSTRAPING COMPLETE]")
    print(f"ADD: `alias DMRC='{__file__}'`")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "bootstrap":
        bootstraping()
        sys.exit()
    try:
        os.execv(VENV_PYT, [VENV_PYT, MAIN] + sys.argv[1:])
    except Exception as e:
        print(e)
        print("RUN `DMRC bootstrap` ")


if __name__ == "__main__":
    main()
