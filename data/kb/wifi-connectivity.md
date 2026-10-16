---
title: Wi-Fi Connectivity
category: network
---

# Wi-Fi Connectivity

## Office networks

| Network       | Who it is for                    | How to connect                               |
|---------------|----------------------------------|----------------------------------------------|
| `CORP-SECURE` | Company laptops                  | Connects automatically using the device certificate |
| `CORP-BYOD`   | Personal phones and tablets      | Sign in with company email and password      |
| `CORP-GUEST`  | Visitors                         | Daily password shown at reception            |

## Company laptop will not join CORP-SECURE

1. Turn Wi-Fi off and on again.
2. Forget the network: **Settings → Network & internet → Wi-Fi → Manage known networks →
   CORP-SECURE → Forget**, then reconnect.
3. `CORP-SECURE` uses the same device certificate as the VPN. If you also see VPN
   certificate errors, run **Renew Device Certificate** from the Software Center (connect via
   a network cable or `CORP-GUEST` first).
4. Restart the laptop.

## Connected but no internet

1. Open a browser and visit any public website; a sign-in page may appear on guest networks.
2. Run the Windows network troubleshooter: right-click the Wi-Fi icon → **Diagnose network
   problems**.
3. Open Command Prompt and run:
   ```
   ipconfig /release
   ipconfig /renew
   ipconfig /flushdns
   ```

## Slow Wi-Fi

- Move closer to an access point or away from microwaves and thick walls.
- Prefer the 5 GHz band; most office access points support it.
- Close large downloads and cloud sync temporarily.
- For video calls, use a wired connection where one is available at your desk.

## Home Wi-Fi

The company does not support home routers. Restart your router, and contact your internet
provider if other devices at home also have no connection.
