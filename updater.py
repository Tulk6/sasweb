import subprocess

def update():
    src = "https://github.com/Tulk6/sasweb.git"

    r = subprocess.Popen(["git", "pull", "origin", "main"])
    
