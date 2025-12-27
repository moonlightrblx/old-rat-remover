import os
import subprocess
import sys
import time
import ctypes

def remove(drive_letter):
    paths = {
        'C': [
            (r'C:\Windows\Resources\svchost.exe', 'svchost.exe'),
            (r'C:\Windows\Resources\spoolsv.exe', 'spoolsv.exe'),
            (r'C:\Windows\Resources\Themes\explorer.exe', 'explorer.exe'),
            (r'C:\Windows\Resources\Themes\icsys.icn.exe', 'icsys.icn.exe')
        ],
        'D': [
            (r'D:\Windows\Resources\svchost.exe', 'svchost.exe'),
            (r'D:\Windows\Resources\spoolsv.exe', 'spoolsv.exe'),
            (r'D:\Windows\Resources\Themes\explorer.exe', 'explorer.exe'),
            (r'D:\Windows\Resources\Themes\icsys.icn.exe', 'icsys.icn.exe')
        ],
        'E': [
            (r'E:\Windows\Resources\svchost.exe', 'svchost.exe'),
            (r'E:\Windows\Resources\spoolsv.exe', 'spoolsv.exe'),
            (r'E:\Windows\Resources\Themes\explorer.exe', 'explorer.exe'),
            (r'E:\Windows\Resources\Themes\icsys.icn.exe', 'icsys.icn.exe')
        ]
    }

    if drive_letter in paths:
        for file_path, process_name in paths[drive_letter]:
            if os.path.exists(file_path):
                try:
                    subprocess.run(['attrib', '-h', '-r', '-s', '/s', '/d', file_path], shell=True)
                    subprocess.run(['wmic', 'process', 'where', f'ExecutablePath=\'{file_path}\'', 'CALL', 'TERMINATE', '/nointeractive'], shell=True)
                    subprocess.run(['del', '/f', '/A:S', file_path], shell=True)
                    subprocess.run(['del', '/f', file_path], shell=True)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    if not is_admin():
        print("ERROR: Run as Admin.")
        sys.exit(1)
    print("--- VERZE CLEANUP START ---")
    time.sleep(3)
    os.system('cls')
    print("--- VERZE CLEANUP START ---")
    current_drive = os.getcwd()[0].upper()
    if current_drive == 'C':
        remove('C')
    elif current_drive == 'D':
        remove('D')
    elif current_drive == 'E':
        remove('E')

    print("Done! explorer.exe (TJprojMain) is now removed")
    os.system("pause")
    print('\ntool made by cloud')
