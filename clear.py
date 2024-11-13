import subprocess,os,sys
def clear():
    if os.name == 'nt':  
        subprocess.run('cls', shell=True)
    else:  
        subprocess.run('clear', shell=True)

if __name__ == "__main__":
    subprocess.run([sys.executable, "start.py"])