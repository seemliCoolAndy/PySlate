# Security policy

PySlate is a local Python learning environment, not a security sandbox. Running untrusted Python code may access resources permitted to the current application/user.

## Reporting a vulnerability

Please do not publish credentials, personal data, or weaponizable exploit details in a public issue. Use GitHub's private vulnerability reporting feature if it is enabled for this repository; otherwise contact the repository owner privately through GitHub and include minimal reproduction steps.

## Scope notes

- Windows code execution uses the current Windows user's permissions.
- Android runs Python in a separate process, but the runner shares the app UID and is not an isolated security sandbox.
- Timeouts and output limits are resource controls, not a guarantee that arbitrary code is safe.
