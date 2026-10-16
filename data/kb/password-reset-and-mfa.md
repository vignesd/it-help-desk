---
title: Password Reset and MFA Enrollment
category: accounts
---

# Password Reset and MFA Enrollment

## Password policy

- Minimum 14 characters.
- Must not contain your name or username.
- Cannot reuse any of your last 10 passwords.
- Passwords expire every 180 days. You get email reminders 14, 7 and 1 day before expiry.

## Reset a forgotten password (self-service)

1. Go to `https://passwordreset.example.com` from any browser (works off the VPN).
2. Enter your company email address.
3. Verify your identity with your registered MFA method (Authenticator app or SMS code).
4. Choose a new password that meets the policy above.
5. Wait 5 minutes, then sign in. On a company laptop that is off the office network,
   connect to the VPN and lock/unlock the computer so it picks up the new password.

## Change a password you still know

On Windows press **Ctrl+Alt+Delete** and choose **Change a password**. On macOS use
`https://passwordreset.example.com` and choose **Change password**.

## Set up MFA (multi-factor authentication)

1. Install **Microsoft Authenticator** on your phone.
2. On a computer, go to `https://mysignins.example.com/security-info`.
3. Click **Add sign-in method** → **Authenticator app** and scan the QR code with your phone.
4. Approve the test notification.
5. Add a phone number as a backup method.

## New phone or lost phone

- **New phone, old phone still available:** add the Authenticator app on the new phone
  using the steps above, then remove the old device from the security-info page.
- **Phone lost or reset:** you cannot complete MFA yourself. Contact the Service Desk so a
  technician can verify your identity and issue a Temporary Access Pass.
