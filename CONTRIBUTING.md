# Contributing to SiteSentry

Thank you for helping improve SiteSentry. The project is designed as a **local-first, deterministic inspection tool**. A contribution should preserve those properties: a user must be able to understand the rules, inspect the code path, and see that the only outbound traffic is a direct request to the target they entered.

## Start locally

Run `./install.sh` on Linux or macOS, or `./install.ps1` from PowerShell on Windows. The installer creates `.venv` and installs the documented Python dependencies. Start the local application with the command shown by the installer, then run the checks below before opening a pull request.

| Task | Linux/macOS | Windows PowerShell |
| --- | --- | --- |
| Python tests | `.venv/bin/python -m pytest` | `& .\.venv\Scripts\python.exe -m pytest` |
| Frontend type check | `pnpm check` | `pnpm check` |
| Frontend production build | `pnpm build` | `pnpm build` |

## Coding style

Keep Python focused, typed where practical, and formatted with standard PEP 8 conventions. Keep every check self-contained and deterministic: do not call third-party APIs, infer risks with ML, add telemetry, expand to broad port ranges, attempt authentication, or implement exploitation behavior. On the frontend, use the existing component and token system, keep keyboard focus visible, and preserve the Paper/Night theme plus reduced-motion behavior.

## Add a check module

Create one file in `backend/checks/` with one clear responsibility, such as `cookie_check.py`. The module should accept a normalized hostname or URL, return a list of finding dictionaries in the existing shape, and use a **fixed documented rule set**. Each finding needs a severity, concise title, plain-English consequence, remediation instruction, and machine-readable evidence.

Next, add focused unit tests under `tests/`; wire the check into `backend/app.py`; and update [docs/SCORING.md](docs/SCORING.md) plus the README scoring table if the new rule affects the grade. Prefer local fixtures or stubbed request sessions in tests so the suite does not depend on an external domain.

## Submit a pull request

Create a focused branch, explain the user-visible behavior in the pull-request description, and include test results. Do not commit `.env` files, local SQLite data, virtual environments, reports with potentially sensitive target information, or generated build directories. Maintainers may ask for a revised deterministic rule, clearer remediation language, or additional test coverage before merging.

## Community expectations

Be respectful, protect sensitive information, and do not use issue discussions or pull requests to share targets that you do not control. Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
