Basic vibe coding of a simple python script that checks your local nVidia GPU driver against the latest online version, and if your version is outdated it fires a windows notification with a hyperlink to download the latest driver. Useful if you're not using the NVIDIA APP

# To get the specific psid and pfid:
- Navigate to [this URL](https://gfwsl.geforce.com/nvidia_web_services/controller.php?com.nvidia.services.Drivers.getMenuArrays/{"pt":1,"driverType":"all"}) and read the response .json 
- The second array (denoted as [1]) contains the family IDs; find your series and add the ID to the URL above. This example uses pst=131 for the 50 series/family of cards, like the 5070Ti, for example:  
https://gfwsl.geforce.com/nvidia_web_services/controller.php?com.nvidia.services.Drivers.getMenuArrays/{"pt":1,"pst":131,"driverType":"all"} 
- In the third array ([2]) you will find the specific model ID, for example 1068 for the 5070Ti
- At the beggining of the script update the psid with your family ID (131 in our example) and the pfid (1068 in our example) to find drivers for your specific card

This will check for Game-Ready WHQL non-beta drivers for Win11
If you're looking for another OS the fifth array [4] in either responses will give you the right OS ID (57 for Win10, 135 for Win11, 12 for Linux, etc.)
The language ID is set to 1033 by default, for English US
