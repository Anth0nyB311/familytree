"""clear the terminal"""
import subprocess
import os
import sys
def clear():
    """clear the terminal based on os"""
    if os.name == 'nt':  # for windows
        subprocess.run('cls', shell=True, check=True)
    else:  # for linux
        subprocess.run('clear', shell=True, check=True)
if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"], check=True)
