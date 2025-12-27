modules = ["os","sys","subprocess","shutil","re","ctypes","time","pathlib","typing","colorama"]
import subprocess, sys
for m in modules:
    try:__import__(m)
    except ImportError:subprocess.check_call([sys.executable,"-m","pip","install",m])
    
import os,sys,subprocess,shutil,re,ctypes,time
from scripts import lw_remover as lw
from scripts import tprjmain_remover as tprj
from pathlib import Path
from typing import List
from colorama import Fore,Style,init
init(autoreset=True)
def printf(t,c=Fore.WHITE,e="\n"):print(f"{c}{t}{Style.RESET_ALL}",end=e)
def menu():
    while True:
        os.system("cls" if os.name=="nt" else "clear")
        printf("\n=== VERZE VIRUS REMOVER ===",Fore.CYAN)
        printf("1. Remove LW",Fore.YELLOW)
        printf("2. Remove Tprjmain (explorer.exe virus)",Fore.YELLOW)
        printf("3. Exit\n",Fore.YELLOW)
        choice=input(Fore.GREEN+"Select an option (1-3): "+Style.RESET_ALL).strip()
        if not choice.isalnum():break
        if choice=="1":printf("\nRunning LW remover...\n",Fore.CYAN);lw.main();break
        elif choice=="2":printf("\nRunning Tprjmain remover...\n",Fore.CYAN);tprj.main();break
        elif choice=="3":printf("Exiting...",Fore.LIGHTBLACK_EX);break
        else:printf("Invalid option. Please try again.",Fore.RED)
    os.system("cls" if os.name=="nt" else "clear")
    printf("Thanks for using Verze Virus Remover.",Fore.GREEN)
if __name__=="__main__":menu()
