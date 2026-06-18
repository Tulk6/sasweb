#!/usr/bin/python3

import subprocess, os

def update():
    src = "https://github.com/Tulk6/sasweb.git"

    r = subprocess.Popen(["git", "pull", "origin", "main"])
    

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    update()
    input("")
