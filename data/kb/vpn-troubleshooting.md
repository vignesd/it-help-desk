---
title: VPN Connection Troubleshooting
category: network
---

# VPN Connection Troubleshooting

The company uses the GlobalConnect VPN client for remote access to internal systems
(intranet, file shares, HR portal). You must be connected to the VPN to reach any
`*.corp.example.com` address from outside the office.

## Connecting for the first time

1. Install GlobalConnect from the Software Center (Windows) or Self Service (macOS).
2. Open GlobalConnect and enter the portal address `vpn.example.com`.
3. Sign in with your company email and password.
4. Approve the MFA push notification on your phone.
5. The icon in the system tray turns green when connected.

## VPN will not connect

1. Check that your normal internet connection works by opening any public website.
2. Restart the GlobalConnect client: right-click the tray icon, choose **Quit**, then reopen it.
3. Confirm the portal address is exactly `vpn.example.com`.
4. If you recently changed your password, sign out of GlobalConnect and sign in again with
   the new password.
5. Restart your computer.

## "Certificate expired" or "Certificate not trusted" error

This means the device certificate on your laptop has expired. Device certificates renew
automatically when the laptop connects to the office network or to the VPN at least once
every 90 days.

1. Open the Software Center and run the **Renew Device Certificate** package.
2. Restart your computer.
3. Try connecting again.
4. If the error persists after renewal, the laptop needs to be re-enrolled by a technician;
   contact the Service Desk.

## VPN connects but internal sites do not load

1. Disconnect and reconnect the VPN.
2. Flush the DNS cache: open Command Prompt and run `ipconfig /flushdns`.
3. Make sure no other VPN software (personal VPNs) is running at the same time.

## VPN keeps disconnecting

- Switch from Wi-Fi to a wired connection if possible, or move closer to your router.
- Disable sleep for network adapters: Device Manager → Network adapters → your adapter →
  Power Management → uncheck "Allow the computer to turn off this device to save power".
- Update GlobalConnect to the latest version from the Software Center.
