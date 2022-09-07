#!/usr/bin/env python3
# Skip to the CONFIGURATION area, around line 22. Big thing, cant miss it.

print("Manifest script v0.2 now running!")

# Import libraries
from pathlib import Path
import argparse
import datetime
import hashlib
import asyncio
import aiohttp
import base64
import os

# The publish action gives us arguments designating the codebase and version
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--codebase", dest="codebase", help="codebase")
parser.add_argument("-v", "--version", dest="version", help="version")
arguments = parser.parse_args()


#################
# CONFIGURATION #
#################
# EDITING PLACE #
#################
cwd = "/var/www/YOUR_PATH_HERE.com" # Path to an exposed working directory (via NGINX or whatever)
buildpath = cwd + "/{}/builds/{}/".format(arguments.codebase, arguments.version) # The path to place the manifest/zip builds
manifestpath = cwd + "/{}/builds/manifest.json".format(arguments.codebase) # The path to the manifest
buildurl = "https://YOUR_URL_HERE.com/{}/builds/{}".format(arguments.codebase, arguments.version) # The URL to the "buildpath"
watchdogurl = "http://localhost:5000" # The URL to your watchdog FROM the server
instance = "" # The instance that you are updating
# Under no circumstances should you EVER make this a STRING.
# Doing so can and will expose your Watchdog API token and
# can allow individuals to control your specific instance.
apitoken = os.getenv("")

# DO NOT EDIT BYOND (heh) THIS POINT
# If you're just the regular sysadmin, don't go BYOND this point (i'll stop) if you aren't going to contribute
# The rest of this script was written by Daemon and some parts patched up by me (eclipse)
# Warning: Code may may give an unknown amount of code-radiation and cause code-cancer

print(f"Creating a manifest.json for a v{arguments.version} {arguments.codebase} codebase!")

TIME = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f-04:00")
manifestfile = open(manifestpath, "w")
SHA = 0

path = Path(buildpath)
manifest = Path(manifestpath)

zips = {
	"linuxarm64": "",
	"linuxx64": "",
	"osxx64": "",
	"winx64": "",
	"client": ""
}

for file in path.glob('*.zip'):
    sha256_hash = hashlib.sha256()
    with open(file, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        print(file.name + " " + sha256_hash.hexdigest())
		# Me when no switch statement in python
        if file.name == "SS14.Server_linux-arm64.zip":
            zips.linuxarm64 = sha256_hash.hexdigest().upper()
        elif file.name == "SS14.Server_linux-x64.zip":
            zips.linuxx64 = sha256_hash.hexdigest().upper()
        elif file.name == "SS14.Server_osx-x64.zip":
            zips.osxx64 = sha256_hash.hexdigest().upper()
        elif file.name == "SS14.Server_win-x64.zip":
            zips.winx64 = sha256_hash.hexdigest().upper()
        elif file.name == "SS14.Client.zip":
            zips.client = sha256_hash.hexdigest().upper()
        print(f"Finished hashing {file.name}!")

print("All files hashed!")
print("Generating manifest.json...")

data = f"""{{
  "builds": {{
    "{arguments.version}": {{
      "server": {{
        "win-x64": {{
          "sha256": "{zips.winx64}",
          "url": "{buildurl}/SS14.Server_win-x64.zip"
        }},
        "linux-arm64": {{
          "sha256": "{zips.linuxarm64}",
          "url": "{buildurl}/SS14.Server_linux-arm64.zip"
        }},
        "osx-x64": {{
          "sha256": "{zips.osxx64}",
          "url": "{buildurl}/SS14.Server_osx-x64.zip"
        }},
        "linux-x64": {{
          "sha256": "{zips.linuxx64}",
          "url": "{buildurl}/SS14.Server_linux-x64.zip"
        }}
      }},
      "time": "{TIME}",
      "client": {
        "sha256": "{zips.client}",
        "url": "{buildurl}/SS14.Client.zip"
      }
    }}
  }}
}}"""

print("Manifest created!")
print(data)
manifestfile.writelines(data)
manifestfile.close()

print("Manifest wrote!")

async def tryupdatewatchdog():
    try:
        # I stole this from MoMMI code lmao
        # Tweaked it a bit, however
        
        url = watchdogurl + f"/instances/{instance}/update"
        authHeader = "Basic " + base64.b64encode(f"{instance}:{apitoken}".encode("ASCII")).decode("ASCII")
        
        async with aiohttp.ClientSession() as session:
            async def load():
                async with session.post(url, headers={"Authorization": authHeader}) as resp:
                    if resp.status != 200:
                        print("Wrong status code: {resp.status}")
                        return
            await asyncio.wait_for(load(), timeout=5)
            
    except asyncio.TimeoutError:
        print("Server timed out while attempting to update watchdog")
        return
    except:
        print("An unknown error occured.")
        return

    print("Updated watchdog!")

if apitoken is None:
    print("Unable to update watchdog instance!")
else:
    tryupdatewatchdog()

# 151 lines of code. but at last i made it tolerable
# v0.1 originally made by daemon, however it was really
# shitty due to the fact that everything was hardcoded
# v0.2 made by me, eclipse/just-a-unity-dev. i unhardcoded
# everything and tried to make watchdog updating workable.
# designed 4 space station 14.
# love you all <3
