---
title: OneDrive Sync Issues
category: storage
---

# OneDrive Sync Issues

OneDrive for Business is the company cloud storage for your personal work files. Your Desktop,
Documents and Pictures folders are backed up to OneDrive automatically. Each employee has 1 TB
of storage.

## OneDrive is not syncing

1. Click the OneDrive cloud icon in the system tray (Windows) or menu bar (macOS) and check the
   status message.
2. If it says **Paused**, click **Resume syncing**.
3. Make sure you are connected to the internet. OneDrive does not need the VPN.
4. Quit OneDrive (cloud icon → **Settings gear → Quit OneDrive**) and start it again from the
   Start menu.
5. Restart your computer.

## Red X or "Sync pending" on files

- A red X means the file could not be uploaded. Hover over the file to see the reason.
- Files that are open in another program upload only after you close them.
- Very large files (over 250 GB) cannot be uploaded.

## Error "The file name is invalid" or "Can't sync this item"

OneDrive does not allow some characters and names.

1. Rename files that contain any of these characters: `" * : < > ? / \ |`
2. File names cannot start or end with a space, or end with a period.
3. Names such as `CON`, `PRN`, `AUX`, `NUL` and `desktop.ini` are not allowed.
4. The full path (folders plus file name) must be shorter than 400 characters. Move deeply
   nested folders closer to the top level.

## Error "Your OneDrive is full"

1. Open the OneDrive website (`onedrive.example.com`) and check **Storage** in the settings.
2. Empty the OneDrive recycle bin; deleted files still count against your storage for 93 days.
3. Move team files to the correct SharePoint or shared drive instead of your personal OneDrive.

## Sync conflict: duplicate files with my computer name

If you edit the same file on two devices before it syncs, OneDrive keeps both copies and adds
your computer name to one of them, for example `Budget-LAPTOP123.xlsx`.

1. Open both files and keep the correct version.
2. Delete the other copy.
3. To avoid conflicts, open shared Office files from OneDrive or Teams and edit them online
   together instead of editing local copies.

## Restore a deleted or overwritten file

1. Go to `onedrive.example.com`.
2. Deleted files: open **Recycle bin**, select the file and click **Restore**. Files are kept for
   93 days.
3. Older versions: right-click the file → **Version history**, then restore the version you need.
