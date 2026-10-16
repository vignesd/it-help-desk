---
title: Outlook and Email Issues
category: email
---

# Outlook and Email Issues

## Outlook will not open or freezes on "Loading profile"

1. Close Outlook completely (check Task Manager for `OUTLOOK.EXE` and end it).
2. Start Outlook in safe mode: press **Win+R**, type `outlook.exe /safe`, press Enter.
3. If safe mode works, a broken add-in is the cause: go to **File → Options → Add-ins →
   COM Add-ins → Go** and untick add-ins one at a time.
4. If safe mode also fails, run **Repair Office** from the Software Center.

## Emails are stuck in the Outbox

- Check you are online (bottom status bar should say **Connected**).
- Attachments over **25 MB** cannot be sent. Share large files with a OneDrive link instead.
- Open the stuck message, remove large attachments, and send again.

## Mailbox is full

Mailboxes are limited to **50 GB**. To free space:
1. Empty **Deleted Items** and **Junk Email**.
2. Use **File → Tools → Mailbox Cleanup** to find large items.
3. Enable **Online Archive**: items older than 2 years move there automatically.

## Not receiving external email

1. Check the **Junk Email** folder and the quarantine digest email.
2. Ask the sender to confirm your address and check for a bounce message.
3. If messages from a trusted sender are quarantined, release them from the digest email
   and click **Allow sender**.

## Shared mailbox does not appear

Shared mailboxes appear automatically up to 60 minutes after access is granted. Restart
Outlook. Access to a shared mailbox must be requested from the mailbox owner.

## Suspicious or phishing email

Do not click links or open attachments. Use the **Report Phishing** button in the Outlook
toolbar. If you already clicked a link or entered your password, change your password
immediately and contact the Service Desk.
