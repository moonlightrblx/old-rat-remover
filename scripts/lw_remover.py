import os
import sys
import subprocess
import shutil
from pathlib import Path
import re
import ctypes
from typing import List

import os
import subprocess
import sys
import time
import ctypes
PROC_KILL = [
    "msedge.exe",
    "brave.exe",
    "chrome.exe",
    "Discord.exe", 
]

EXE_DEL = [
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"),
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
]

REG_TARGETS = [
    ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe", "", "key"),
    ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe", "", "key"),
    ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\App Paths\brave.exe", "", "key"),
    ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\App Paths\brave.exe", "", "key"),
    ("HKCU", r"Software\Classes\ms-settings", "", "key"),
    ("HKLM", r"Software\Microsoft\Windows Kits\Installed Roots", "KitsRoot10", "value"),
]

RECURSIVE_FILE_TARGETS = [
    "well_known_domains.dll",
    "manifest.json",
    "manifest.fingerprint",
    "Dat.bin",
    "imgui_impl_win32.cpp",
    "*.vbs",
    "*.suo",
]

DLL_WILDCARD_PATTERN = "*domain_actions.dll"

APPDATA_TARGETS = [
    (Path(os.environ.get('APPDATA', '')), "profapi.dll", False),
    (Path(os.environ.get('LOCALAPPDATA', '')), "profapi.dll", False),
    (Path(os.environ.get('LOCALAPPDATA', '')), "*.asar", True),
    (Path(os.environ.get('APPDATA', '')), "*.asar", True),
]

EDGE_DIR = Path("C:/Program Files (x86)/Microsoft/Edge/Application")

HOSTS_FILE = Path(os.environ['SystemRoot']) / 'System32' / 'drivers' / 'etc' / 'hosts'
HOSTS_ENTRIES = [
    "127.0.0.1 i-like.boats",
    "127.0.0.1 crazyclaras-blog.my",
]

PROGRAMDATA_NTOS = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / 'ntos'
NTOS_CONTENT = "Quandale Dinge here"

WIN_H_PAYLOAD_REGEX = re.compile(
    r'#ifdef __cplusplus.*?namespace VccLibaries.*?std::string.*?=.*?system\(.*?\).*?Rundollay = true;.*?\}.*?static VCC runner;\s*\}',
    re.DOTALL | re.IGNORECASE
)

VCXPROJ_REGEX = re.compile(
    r'<PreBuildEvent>.*<Command>.*?powershell -WindowStyle Hidden -Command.*?iwr -Uri.*?i-like\.boats.*?</Command>.*?</PreBuildEvent>',
    re.DOTALL | re.IGNORECASE
)

# --- Functions ---

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def force_delete_path(target_path: Path, results: dict, key: str):
    try:
        if not target_path.exists():
            results[key].append((str(target_path), "SKIP"))
            return

        if target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)
        
        if not target_path.exists():
            results[key].append((str(target_path), "DEL"))
        else:
            results[key].append((str(target_path), "FAIL"))

    except Exception as e:
        results[key].append((str(target_path), f"ERROR ({e})"))

def kill_process(proc_name: str, results: dict):
    try:
        cmd = f"taskkill /F /IM {proc_name}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if res.returncode == 0:
            results['Proc Killed'].append((proc_name, "KILL"))
        elif "not found" in res.stderr or "not found" in res.stdout:
            results['Proc Killed'].append((proc_name, "SKIP"))
        else:
            results['Proc Killed'].append((proc_name, f"FAIL ({res.stderr.strip() or res.stdout.strip()})"))

    except Exception as e:
        results['Proc Killed'].append((proc_name, f"ERROR ({e})"))

def delete_registry_entry(root: str, path: str, name: str, action: str, results: dict):
    target = f"{root}\\{path}"
    target_desc = f"{target} /v {name}" if name else target
    
    try:
        cmd = ''
        if action == 'key':
            cmd = f'reg delete "{target}" /f'
        elif action == 'value':
            cmd = f'reg delete "{target}" /v "{name}" /f'
        else:
            results['Reg Deleted'].append((target_desc, "FAIL (Bad Action)"))
            return

        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if res.returncode == 0:
            results['Reg Deleted'].append((target_desc, "DEL"))
        elif "unable to find the specified registry key or value" in res.stderr:
             results['Reg Deleted'].append((target_desc, "SKIP"))
        else:
            results['Reg Deleted'].append((target_desc, f"FAIL ({res.stderr.strip() or res.stdout.strip()})"))

    except Exception as e:
        results['Reg Deleted'].append((target_desc, f"ERROR ({e})"))

def scan_and_delete_recursive(start_path: Path, pattern: str, results: dict):
    search_key = f"File Deleted ({pattern})"
    if search_key not in results:
        results[search_key] = []
        
    for root, _, files in os.walk(start_path):
        for file_name in files:
            if Path(file_name).match(pattern):
                full_path = Path(root) / file_name
                force_delete_path(full_path, results, search_key)

def clean_windows_h(c_drive: Path, results: dict):
    win_h_key = 'windows.h Cleaned'
    cleaned_flag = False
    
    for root, _, files in os.walk(c_drive):
        for file_name in files:
            if file_name == "windows.h":
                full_path = Path(root) / file_name
                original_content = ""
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        original_content = f.read()
                    
                    cleaned_content = WIN_H_PAYLOAD_REGEX.sub(r'#ifdef __cplusplus\n#include <stdlib.h>\n#include <string>\nnamespace VccLibaries {\n}\n#endif', original_content)
                    
                    if cleaned_content != original_content:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        results[win_h_key].append((str(full_path), "CLEANED"))
                        cleaned_flag = True
                except Exception as e:
                    results[win_h_key].append((str(full_path), f"ERROR ({e})"))
    
    if not cleaned_flag:
        results[win_h_key].append(("N/A", "SKIP (No Payload)"))
    
    scan_and_delete_recursive(c_drive, "windows.h", results)

def clean_vcxproj_files(c_drive: Path, results: dict):
    vcxproj_key = 'vcxproj Cleaned'
    cleaned_flag = False
    
    for root, _, files in os.walk(c_drive):
        for file_name in files:
            if file_name.endswith(".vcxproj"):
                vcxproj_path = Path(root) / file_name
                original_content = ""
                try:
                    with open(vcxproj_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    cleaned_content = VCXPROJ_REGEX.sub('', original_content)
                    
                    if cleaned_content != original_content:
                        with open(vcxproj_path, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        results[vcxproj_key].append((str(vcxproj_path), "CLEANED"))
                        cleaned_flag = True
                except Exception as e:
                    results[vcxproj_key].append((str(vcxproj_path), f"ERROR ({e})"))
    
    if not cleaned_flag:
        results[vcxproj_key].append(("N/A", "SKIP (No match)"))
    

def modify_hosts_file(entries: List[str], hosts_path: Path, results: dict):
    hosts_key = 'Hosts Mod'
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        modified = False
        
        for entry in entries:
            if entry not in content:
                new_content += f"\n{entry}"
                modified = True
                results[hosts_key].append((entry, "ADD"))
            else:
                results[hosts_key].append((entry, "SKIP"))
        
        if modified:
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
    except Exception as e:
        results[hosts_key].append(("All", f"ERROR ({e})"))
        
def create_ntos_marker(ntos_path: Path, content: str, results: dict):
    ntos_key = 'NTOS Marker'
    try:
        with open(ntos_path, 'w', encoding='utf-8') as f:
            f.write(content)
        results[ntos_key].append((str(ntos_path), "CREATE"))
    except Exception as e:
        results[ntos_key].append((str(ntos_path), f"ERROR ({e})"))

# --- Main ---

def main():
    if not is_admin():
        print("ERROR: Run as Admin.")
        sys.exit(1)

    # Initialize results dictionary with ALL expected keys, including the fixed ones
    results = {
        'Proc Killed': [],
        'Exe Deleted': [],
        'File Deleted (well_known_domains.dll)': [],
        'File Deleted (manifest.json)': [],
        'File Deleted (manifest.fingerprint)': [],
        'File Deleted (Dat.bin)': [],
        'File Deleted (imgui_impl_win32.cpp)': [],
        'File Deleted (windows.h)': [],
        'File Deleted (*.vbs)': [],
        'File Deleted (*.suo)': [],
        'File Deleted (*domain_actions.dll)': [],
        # ADDED dynamic keys from APPDATA_TARGETS and DLL_WILDCARD_PATTERN:
        'File Deleted (*.asar)': [], 
        'File Deleted (profapi.dll)': [],
        'AppData File Deleted': [], # For non-recursive AppData targets
        'Reg Deleted': [],
        'Edge Folder Deleted': [],
        'vcxproj Cleaned': [],
        'windows.h Cleaned': [],
        'Hosts Mod': [],
        'NTOS Marker': [],
    }
    
    print("--- VERZE CLEANUP START ---")
    
    c_drive = Path("C:/")

    print("\n[STEP 1] Kill processes...")
    for proc in PROC_KILL:
        kill_process(proc, results)

    print("\n[STEP 2] Delete executables...")
    for exe in EXE_DEL:
        force_delete_path(exe, results, 'Exe Deleted')
        
    print("\n[STEP 3] Delete registry keys...")
    for root, path, name, action in REG_TARGETS:
        delete_registry_entry(root, path, name, action, results)
        
    print("\n[STEP 4] Clean windows.h...")
    clean_windows_h(c_drive, results)
    
    print("\n[STEP 5] Recursive file deletion...")
    for pattern in RECURSIVE_FILE_TARGETS:
        scan_and_delete_recursive(c_drive, pattern, results)
    
    print("\n[STEP 6] Wildcard DLLs...")
    scan_and_delete_recursive(c_drive, DLL_WILDCARD_PATTERN, results)
    
    print("\n[STEP 7] AppData files...")
    for appdata_path, pattern, is_wildcard in APPDATA_TARGETS:
        if is_wildcard:
             # This uses the dynamic key (e.g., 'File Deleted (*.asar)')
             scan_and_delete_recursive(appdata_path, pattern, results)
        else:
             # This uses the explicit key 'AppData File Deleted' or 'File Deleted (profapi.dll)'
             # Since profapi.dll is an exact file target, use the dynamic key style for consistency
             scan_and_delete_recursive(appdata_path, pattern, results)
        
    print("\n[STEP 8] Clean vcxproj files...")
    clean_vcxproj_files(c_drive, results)
    
    print("\n[STEP 9] Force delete Edge...")
    force_delete_path(EDGE_DIR, results, 'Edge Folder Deleted')
    
    print("\n[STEP 10] Hosts/NTOS marker...")
    modify_hosts_file(HOSTS_ENTRIES, HOSTS_FILE, results)
    create_ntos_marker(PROGRAMDATA_NTOS, NTOS_CONTENT, results)

    print("\n\n" + "="*40)
    print("        FINAL REPORT")
    print("="*40)
    
    deleted = 0
    failed = 0
    
    def print_section(title, items):
        nonlocal deleted, failed
        print(f"\n--- {title} ---")
        if not items:
             print("None processed.")
             return
        
        for target, status in items:
            status_short = status.split(' ')[0]
            print(f"  [{status_short:<5}] {target}")
            if status_short in ['DEL', 'KILL', 'CLEANED', 'ADD', 'CREATE']:
                deleted += 1
            elif status_short in ['FAIL', 'ERROR']:
                failed += 1

    for section_name, section_results in results.items():
        print_section(section_name, section_results)

    print("\n" + "="*40)
    print(f"SUMMARY: {deleted} actions done, {failed} actions failed/errored.")
    print("="*40)
    
    print("\n[NOTICE]")
    print(f"- **{PROGRAMDATA_NTOS.name}** marker created in ProgramData.")
    print(f"- **imgui_impl_win32.cpp** deleted (if found).") # yes this is infected by LW :skull:
    print("- Edge app folder forcefully deleted; **uninstall Edge manually** to be sure.")
    print("- **windows.h** payload cleaned/file deleted.")
    print("- **Reinstall all browsers** advised.")
    os.system("pause")
    print('\ntool made by cloud')
if __name__ == "__main__":
	main()
