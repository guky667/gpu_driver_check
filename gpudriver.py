"""
Script: NVIDIA Driver Version Checker
Author: Gemini Large Language Model (LLM) by Google
Created: August 16, 2025

Description:
This script checks the local NVIDIA Display Driver version and compares it with the latest
version available from the official NVIDIA website. If a newer version is found, it
provides a pop-up notification with a clickable link to the download page.

License:
This work is released into the public domain. You are free to use, modify, and distribute
this script without any restrictions.
"""

import os
import re
import requests
import webbrowser
import ctypes

# Note: You may need to install the 'requests' library first.
# Run 'pip install requests' in your terminal if you encounter an error.

def compare_versions(local_version, online_version):
    local_parts = tuple(map(int, local_version.split('.')))
    online_parts = tuple(map(int, online_version.split('.')))
    
    if online_parts > local_parts:
        return 1
    elif online_parts == local_parts:
        return 0
    else:
        return -1

base_path = r'C:\Program Files\NVIDIA Corporation\Installer2'
search_prefix = 'Display.Driver'
target_file = 'DisplayDriver.nvi'

local_version = None
online_version = None
driver_id = None

try:
    matching_folders = [
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and d.startswith(search_prefix)
    ]
    
    if matching_folders:
        newest_folder = max(matching_folders, key=lambda d: os.path.getctime(os.path.join(base_path, d)))
        file_path = os.path.join(base_path, newest_folder, target_file)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                version_pattern = re.compile(r'<string\s+name="version"\s+value="([^"]+)"')
                match = version_pattern.search(content)
                if match:
                    local_version = match.group(1)
    
    if local_version:
        url = "https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=120&pfid=942&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&upCRD=0&qnf=0&ctk=null&sort1=1&numberOfResults=1"
        response = requests.get(url)
        json_response = response.json()
        
        online_version = json_response['IDS'][0]['downloadInfo']['Version']
        driver_id = json_response['IDS'][0]['downloadInfo']['ID']

except Exception as e:
    print(f"An error occurred: {e}")

if local_version and online_version and driver_id:
    comparison = compare_versions(local_version, online_version)
    
    if comparison == 1:
        download_url = f"https://www.nvidia.com/en-us/drivers/details/{driver_id}/"
        
        # Use a Yes/No message box style
        # 0x04 is MB_YESNO, 0x40 is MB_ICONINFORMATION
        result = ctypes.windll.user32.MessageBoxW(
            0,
            f"A new driver version ({online_version}) is available! Your current version is {local_version}.\n\nWould you like to open the download page?",
            "NVIDIA Driver Update",
            0x04 | 0x40
        )
        
        # Check if the "Yes" button (IDYES which is 6) was clicked
        if result == 6:
            webbrowser.open(download_url)
    else:
        print("Driver is up to date.")
elif local_version is None:
    print("Could not retrieve local driver version.")
elif online_version is None:
    print("Could not retrieve online driver version.")
