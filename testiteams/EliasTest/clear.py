import subprocess,os
def clear():
    if os.name == 'nt':  
        subprocess.run('cls', shell=True)
    else:  
        subprocess.run('clear', shell=True)