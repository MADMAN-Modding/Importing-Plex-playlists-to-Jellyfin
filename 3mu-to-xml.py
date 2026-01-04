import xml.etree.ElementTree as ET
from datetime import datetime

# --- Input .m3u file ---
m3u_file = "MyPlaylist.m3u"  # replace with your actual file path
output_file = "playlist.xml"
user_id = "USER_ID"  # replace with your Jellyfin user ID

# --- Read file paths from M3U ---
file_paths = []
with open(m3u_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):  # skip empty lines and comments
            file_paths.append(line)

# --- Create root XML element ---
item = ET.Element("Item")

# Basic metadata
ET.SubElement(item, "Added").text = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
ET.SubElement(item, "LockData").text = "false"
ET.SubElement(item, "LocalTitle").text = "My Tunes"
ET.SubElement(item, "RunningTime").text = "0"  # optional
ET.SubElement(item, "Genres")  # empty genres
ET.SubElement(item, "OwnerUserId").text = user_id

# Playlist items container
playlist_items = ET.SubElement(item, "PlaylistItems")

for path in file_paths:
    playlist_item = ET.SubElement(playlist_items, "PlaylistItem")
    ET.SubElement(playlist_item, "Path").text = path

# Playlist media type
ET.SubElement(item, "PlaylistMediaType").text = "Audio"

# --- Convert to XML string with declaration ---
xml_str = ET.tostring(item, encoding="utf-8")
xml_pretty = b'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n' + xml_str

# --- Save to file ---
with open(output_file, "wb") as f:
    f.write(xml_pretty)

print(f"Jellyfin playlist XML generated successfully: {output_file}")
