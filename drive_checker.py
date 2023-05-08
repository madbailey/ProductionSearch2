import os
## this just checks if the user is connected to a shared drive 
def is_drive_connected(drive_letter):
    drive = f"{drive_letter}:\\"
    return os.path.exists(drive)
