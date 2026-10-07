# Password Reset

## Department
IT Support

## Document Type
Student support knowledge article

## Purpose
Guide students through safe password recovery while keeping authentication secrets outside the support workflow.

## Overview
Password recovery should use the university's approved self-service reset mechanism whenever one exists. The Copilot can explain the process at a general level, but it must not invent recovery URLs, reset requirements, password complexity rules, or waiting periods.

A password reset is different from an account unlock. A student may know the current password and still be unable to authenticate because the account is locked or another identity-service problem exists.

## Common Questions

### I forgot my password.
Use the university's approved password-reset option and follow its identity-verification steps. If the recovery method is unavailable or the reset fails, contact IT Support.

### I did not receive the password-reset message.
First verify that the recovery process was submitted successfully and that the student is checking the approved recovery channel. The Copilot must not expose or guess recovery information. If no recovery message arrives after the normal system process, escalate.

### I changed my password but still cannot log in.
Confirm that the student is using the new password and the correct portal. A stale browser session can sometimes interfere with testing. If the new password is rejected after a clean retry, route the issue to IT Support.

### Can I send my password to support?
No. Support staff should never request or store a student's password.

## Step-by-Step Procedure

1. Identify whether the student needs a forgotten-password reset or is reporting a separate login problem.
2. Direct the student to the university's approved password-reset flow.
3. Follow the identity-verification process presented by the authorized system.
4. Create a new password according to the system's current requirements.
5. Retry the portal login using the new credential.
6. If login succeeds, no further credential information should be collected.
7. If recovery fails, the recovery channel is unavailable, or the account appears locked, escalate to IT Support.

## Requirements
The student may need an account identifier and access to the recovery method configured in the university identity system. The exact requirements are system-specific and should not be invented by the Copilot.

For support escalation, useful non-secret information includes:
- account identifier or support-safe identifier, where permitted;
- approximate time of reset attempt;
- exact error message;
- whether the reset flow was reached successfully;
- whether a recovery message was received;
- browser/device used.

Never collect:
- current password;
- new password;
- one-time authentication codes;
- security answers or recovery secrets;
- full authentication tokens.

## Troubleshooting

**Reset link is invalid or expired:** start a new approved reset attempt rather than reusing an old link.

**Recovery method is inaccessible:** escalate to IT Support because identity verification may require an authorized manual process.

**Reset succeeds but login fails:** retry in a clean browser session and confirm the correct portal. If the issue remains, escalate.

**Account may be locked:** do not repeatedly submit credentials. Escalate or follow the documented unlock process if one is explicitly available.

**Student reports suspicious password-reset activity:** treat the event as a security concern and escalate promptly rather than continuing normal troubleshooting.

## Important Rules
The Copilot must never request a password or authentication secret. It must not tell a student to send credentials through chat, email, or a ticket. It must not claim a reset was completed unless an authoritative system confirms completion.

The Copilot must also avoid inventing password requirements. Statements such as minimum length, character requirements, expiration periods, or lockout thresholds require current approved documentation.

## When to Escalate
Escalate when:
- identity verification fails;
- the recovery method is unavailable;
- reset attempts repeatedly fail;
- the account appears locked;
- the student reports unauthorized reset activity;
- the student cannot regain access to a critical service;
- a manual account change is required.

## Information to Collect
Collect only support-safe diagnostics: approximate time, error text, service, device/browser, and whether the approved reset process was attempted.

## Related Topics
- Portal Login
- Technical Support
- General Student Support
