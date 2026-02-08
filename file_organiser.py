# ============================================================
#
#
# 1. Load configuration from a JSON file
#
# 2. Classify files based on extension
#    - Identify file type (images, documents, PDFs, videos, etc.)
#
# 4. Create destination folders if they do not exist
#    - Automatically generate required directories
#    - Ensure safe and organized folder structure
#
# 5. Move files to appropriate folders
#    - Relocate files based on classification rules
#    - Handle naming conflicts safely (overwrite / rename)
#
# 6. Run as a background process (daemon-like behavior)
#    - Execute continuously without user interaction
#    - Minimize resource usage while running
#


#What we are not going to do:

# 7. Log activities and errors
#    - Record file movements
#    - Log warnings and exceptions for debugging
#
# 8. Support future enhancements
#    - Enable auto-start on system boot
#    - Extend rules for advanced file handling
# ============================================================

import os
import json
import shutil
import time

#Configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

FOLDER_PATH = os.path.expanduser(CONFIG['folder_paths'])
SCAN_INTERVAL = CONFIG["scan_interval"]
FOLDERS = CONFIG["folders"]

#create folders
def create_folder():
    for folder in FOLDERS.keys():
        path = os.path.join(FOLDER_PATH, folder)
        os.makedirs(path, exist_ok=True)


 #check if file is valide to be moved
def is_valid_file(filename):
    if filename.startswith("."):
        return False
    if filename.endswith((".crdownload", ".part")):
        return False
    return True

 #getting the valid destination
def get_destination(filename):
    ext = os.path.splitext(filename)[1].lower()
    for folder, extensions in FOLDERS.items():
        if ext in extensions:
            return os.path.join(FOLDER_PATH, folder)
    return os.path.join(FOLDER_PATH, "Others")

 # moving function
def save_move(src, dst):
    base, ext = os.path.splitext(dst)
    counter = 1
    new_dst = dst
    while os.path.exists(new_dst):
        new_dst = f"{base}_{counter}{ext}"
        counter +=1
    shutil.move(src, new_dst)

 #avoid crash by safe move
def move_file(filename):
    source = os.path.join(FOLDER_PATH, filename)
    if os.path.isdir(source):
        return
    if not is_valid_file(filename):
        return
    destination = get_destination(filename)
    dest_path = os.path.join(destination, filename)
    save_move(source, dest_path)



 #move all the files at firt execution
def scan_once():
    for item in os.listdir(FOLDER_PATH):
        move_file(item)



 #core logic for looping
def main():
    print("File organizer started.....")
    create_folder()
    scan_once()
    known_files = set(os.listdir(FOLDER_PATH))
    
    while True:
        time.sleep(SCAN_INTERVAL)
        current_files = set(os.listdir(FOLDER_PATH))
        new_files = current_files - known_files
        for filename in new_files:
            move_file(filename)
        if new_files:
            print(f"{len(new_files)} file moved")
        known_files = current_files


if __name__ == "__main__":
    main()


