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

import os
import re
import requests

# ----------------------------------------------------------------------
# 1. Replace win10toast with winotify
# ----------------------------------------------------------------------
from winotify import Notification, audio

def show_driver_update_toast(local_version: str, online_version: str, driver_id: str) -> None:
    """
    Show a Windows toast notification using the winotify library.
    The toast contains the current & latest driver versions and offers an action to open
    the NVIDIA driver download page.

    Parameters
    ----------
    local_version : str
        The version string of the driver installed on this machine.
    online_version : str
        The most recent driver version reported by NVIDIA’s API.
    driver_id : str
        Unique identifier for the driver (used to build the download URL).
    """
    # Build the download link that will be shown in the toast and opened when the user clicks it.
    download_url = f"https://www.nvidia.com/en-us/drivers/details/{driver_id}/"

    title = f"A newer driver is available!"
    message = (
        f"Current version: {local_version}\n"
        f"Latest version : {online_version}"
    )

    # Create the toast
    toast = Notification(
        app_id="NVIDIA Driver Notifier",
        title=title,
        msg=message,
    )
    # Optional: add an icon if you have one (uncomment and provide path)
    # toast.set_icon(r"path\to\icon.ico")

    # Add a clickable action that opens the download page
    toast.add_actions(label="Open link to driver", launch=download_url)

    # Set a default notification sound – optional
    toast.set_audio(audio.Default, loop=False)

    # Show the toast
    toast.show()


def compare_versions(local_version: str, online_version: str) -> int:
    """
    Compare two dotted‑decimal version strings.

    Returns
    -------
    int
        1 if online_version > local_version,
        0 if both are equal,
       -1 if online_version < local_version.
    """
    local_parts = tuple(map(int, local_version.split(".")))
    online_parts = tuple(map(int, online_version.split(".")))

    if online_parts > local_parts:
        return 1
    elif online_parts == local_parts:
        return 0
    else:
        return -1


# ----------------------------------------------------------------------
# 2. Paths & constants for the local NVIDIA driver installation
# ----------------------------------------------------------------------
BASE_PATH = r"C:\Program Files\NVIDIA Corporation\Installer2"
SEARCH_PREFIX = "Display.Driver"
TARGET_FILE = "DisplayDriver.nvi"

local_version: str | None = None
online_version: str | None = None
driver_id: str | None = None

try:
    # Find the newest driver folder that matches the expected naming convention.
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

        # Read the local driver version from the .nvi file
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'<string\s+name="version"\s+value="([^"]+)"', content)
                if match:
                    local_version = match.group(1)

    # Query NVIDIA’s public API for the latest driver information
    if local_version:
        url = (
            "https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/"
            "services/AjaxDriverService.php?func=DriverManualLookup&psid=120"
            "&pfid=942&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1"
            "&dch=1&upCRD=0&qnf=0&ctk=null&sort1=1&numberOfResults=1"
        )
        response = requests.get(url)
        data = response.json()

        online_version = data["IDS"][0]["downloadInfo"]["Version"]
        driver_id = data["IDS"][0]["downloadInfo"]["ID"]

except Exception as exc:
    print(f"[ERROR] {exc}")

# ----------------------------------------------------------------------
# 3. Decision logic – show toast if a newer driver exists
# ----------------------------------------------------------------------
if local_version and online_version and driver_id:
    comp = compare_versions(local_version, online_version)

    if comp == 1:      # newer driver available (according to original code)
        show_driver_update_toast(local_version, online_version, driver_id)
    else:
        print("✅ Driver is up to date.")
elif not local_version:
    print("[WARN] Could not read local driver version.")
else:
    print("[WARN] Could not fetch latest driver info from NVIDIA.")
