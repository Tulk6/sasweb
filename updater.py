#!/usr/bin/python3

import subprocess

def update():
    src = "https://github.com/Tulk6/sasweb.git"

    r = subprocess.Popen(["git", "pull", "origin", "main"])
    

if __name__ == '__main__':
    update()
