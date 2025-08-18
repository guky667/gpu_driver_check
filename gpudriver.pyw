# Update psid and pfid for your specific card - also you can change the OS version and language if needed; detailed instructions in the ReadMe
url = (
    "https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup"
    "&psid=131"          # Family (series, like 50)
    "&pfid=1068"         # Model (like 5070Ti)
    "&osID=135"          # Win11
    "&languageCode=1033" # English US
    "&beta=0"            # No beta drivers
    "&isWHQL=1"          # WHQL cert for Windows from Microsoft
    "&dltype=-1"
    "&dch=1"             # Lightweight modular driver (just driver, without nVidia App or other auxiliary components)
    "&upCRD=0"           # Something about CUDA, I think...
    "&qnf=0"
    "&ctk=null"          # Something else about CUDA, idk, man!
    "&sort1=1"
    "&numberOfResults=1"
)

"""
NVIDIA Driver Update Notifier (winotify version)
Author: Gemini LLM + ChatGPT
Created: 2025‑08‑16

Description:
    * Checks the locally installed NVIDIA driver.
    * Compares it with the latest driver from NVIDIA’s API.
    * If a newer version exists shows a Windows toast with a hyperlink to that driver.

License:
    Public domain – feel free to copy, modify or distribute.
"""

import os, re, requests
from winotify import Notification, audio

BASE_PATH = r"C:\Program Files\NVIDIA Corporation\Installer2"
SEARCH_PREFIX = "Display.Driver"
TARGET_FILE = "DisplayDriver.nvi"

local_version: str | None = None
online_version: str | None = None
driver_id: str | None = None


def show_driver_update_toast(local_version: str, online_version: str, driver_id: str) -> None:
    download_url = f"https://www.nvidia.com/en-us/drivers/details/{driver_id}/"

    title = f"A newer driver is available!"
    message = (
        f"Current version: {local_version}\n"
        f"Latest version : {online_version}"
    )

    toast = Notification(
        app_id="NVIDIA Driver Notifier",
        title=title,
        msg=message,
    )

    toast.add_actions(label="Open link to driver", launch=download_url)
    toast.set_audio(audio.Default, loop=False)

    toast.show()


def compare_versions(local_version: str, online_version: str) -> int:
    local_parts = tuple(map(int, local_version.split(".")))
    online_parts = tuple(map(int, online_version.split(".")))

    if online_parts > local_parts:
        return 1
    elif online_parts == local_parts:
        return 0
    else:
        return -1

try:
    matching_folders = [
        d for d in os.listdir(BASE_PATH)
        if os.path.isdir(os.path.join(BASE_PATH, d)) and d.startswith(SEARCH_PREFIX)
    ]

    if matching_folders:
        newest_folder = max(
            matching_folders,
            key=lambda d: os.path.getctime(os.path.join(BASE_PATH, d)),
        )
        file_path = os.path.join(BASE_PATH, newest_folder, TARGET_FILE)

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'<string\s+name="version"\s+value="([^"]+)"', content)
                if match:
                    local_version = match.group(1)

    if local_version:
        response = requests.get(url)
        data = response.json()

        online_version = data["IDS"][0]["downloadInfo"]["Version"]
        driver_id = data["IDS"][0]["downloadInfo"]["ID"]

except Exception as exc:
    print(f"[ERROR] {exc}")

if local_version and online_version and driver_id:
    comp = compare_versions(local_version, online_version)

    if comp == 1:
        show_driver_update_toast(local_version, online_version, driver_id)
    else:
        print("✅ Driver is up to date.")
elif not local_version:
    print("[WARN] Could not read local driver version.")
else:
    print("[WARN] Could not fetch latest driver info from NVIDIA.")
