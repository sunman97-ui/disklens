# Security Policy

DiskLens is a file analysis and deletion tool. We take security and the safety of user data extremely seriously.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability (e.g., a bug that could bypass safety guards to delete system-critical files), please report it responsibly by:

1. Emailing the maintainer at sunman97@live.co.uk with a detailed description of the vulnerability.
2. Including steps to reproduce the issue (using mocked environments where possible).
3. Allowing time for a fix to be developed and disclosed.

## Safety Architecture

DiskLens employs multiple layers of safety:
- **Hardcoded Blocklists**: Prevents scanning or modifying critical Windows directories.
- **Safe Root Enforcement**: Only allows scanning in specific user-defined areas.
- **Recycle Bin Integration**: Deletions are sent to the system trash via `send2trash`, not permanently deleted.
- **Mocked Tests**: Our CI pipeline includes tests that verify these guards on every push.

---
Thank you for helping us keep DiskLens safe for everyone.
