---
name: Python runtime alignment
description: Environment-specific dependency behavior when the uploaded project specifies a Python minor version.
---

The project dependencies must be installed for the same Python minor version used by the workflow; packages installed into a 3.10 library are not visible to the active 3.11 interpreter.

**Why:** The uploaded configuration selected Python 3.11 while the first dependency installation landed in the 3.10 library, causing imports such as Flask and Requests to fail even though installation reported success.

**How to apply:** Confirm the runtime selected by `.python-version` and `.replit` before installing packages, then run an import check with the exact interpreter used by the workflow.