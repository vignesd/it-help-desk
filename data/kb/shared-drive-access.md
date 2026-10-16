---
title: Shared Drive and Folder Access
category: access
---

# Shared Drive and Folder Access

Department files are stored on network shared drives under `\\files.corp.example.com\`. Access is
granted per department and approved by the folder owner, usually your manager.

## Request access to a shared folder

1. Open the IT Self-Service Portal (`it.example.com`) and choose **Request access → Shared folder**.
2. Enter the full folder path, for example `\\files.corp.example.com\Finance\Reports`.
3. Choose **Read** (view only) or **Modify** (create and edit files).
4. Submit. The folder owner receives an approval request. After approval, access is usually active
   within 2 hours.
5. Sign out of Windows and sign back in so the new permission takes effect.

## Map a network drive (Windows)

1. Open File Explorer and click **This PC**.
2. Click **... → Map network drive**.
3. Choose a drive letter and enter the folder path, for example `\\files.corp.example.com\Finance`.
4. Check **Reconnect at sign-in** and click **Finish**.

On macOS, open Finder, press **Cmd + K**, enter `smb://files.corp.example.com/Finance` and click
**Connect**.

## Error "Access is denied" or "You don't have permission to access this folder"

1. Confirm the access request was approved in the Self-Service Portal under **My requests**.
2. If it was approved less than 2 hours ago, wait, then sign out and sign back in.
3. If you were recently moved to a new department, your old access may have been removed. Submit a
   new request for the folders you need.
4. If you still get the error, contact the Service Desk with the exact folder path.

## Error "Windows cannot access \\files.corp.example.com" or the drive shows a red X

1. Shared drives only work on the office network or through the VPN. Connect to the VPN when
   working remotely.
2. Open the path again in File Explorer; mapped drives sometimes reconnect only when opened.
3. If you recently changed your password, sign out of Windows and sign in again.
4. Restart your computer.

## Recover a deleted file on a shared drive

Shared drives keep snapshots for 30 days.

1. Right-click the folder that contained the file and choose **Properties → Previous Versions**.
2. Select a version from before the file was deleted and click **Open** to browse it.
3. Copy the file back to the original folder.
