---
title: Account Lockout
category: accounts
---

# Account Lockout

Your account locks automatically after **5 failed sign-in attempts within 10 minutes**.
A locked account unlocks itself after **30 minutes**.

## Signs that your account is locked

- The sign-in screen says "The referenced account is currently locked out".
- Outlook, Teams and the VPN all keep asking for your password.

## Unlock your account

1. Wait 30 minutes for the automatic unlock, **or**
2. Go to `https://passwordreset.example.com`, choose **Unlock my account**, and verify with MFA.

## Account keeps locking again

Repeated lockouts are almost always caused by an old password saved on a device.

1. Phone: open the mail app settings and update or remove your company email account, then
   add it again with the new password.
2. Windows: open **Credential Manager** → **Windows Credentials** and remove entries for
   `corp.example.com`, Outlook and Teams.
3. Sign out of Teams and Outlook on every device and sign in again.
4. Disconnect any mapped network drives and reconnect them.

If the account still locks more than twice in one day after these steps, contact the
Service Desk so the lockout source can be traced.
