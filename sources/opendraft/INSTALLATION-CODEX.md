# OpenDraft — installed source and browser companion

Upstream: https://github.com/federicodeponte/opendraft

Version: **1.8.1**. Snapshot: `39b21f74b3f52c34d5d771c508c8ad80f965d35f`.
Installation and verification date: **2026-11-10**.

## What is original

The repository ships a Python research engine and an interactive **terminal CLI**, not a web application. The complete original engine, CLI screens, prompts, templates, documentation, examples and tests are retained. OpenPaper is a separate hosted product linked from upstream; its web UI is not included in this repository or this package.

`codex-web/` is an explicitly added browser companion. It runs the installed original CLI and exporters as real subprocesses, stores runs and files on disk, and reports failures. It does not simulate AI output. A temporary protected Vercel preview was subsequently launched; see CLOUD-PREVIEW.md for its expiry and resume instructions.

## Start on your computer

Requirements: Python 3.10 or newer (tested with 3.12), internet for first installation and model/research calls. Use a terminal you can keep open.

**Windows:** install Python with the Python launcher, extract the ZIP, then double-click `Start-Windows.cmd`.

**macOS / Linux:** extract the ZIP, open a terminal in this folder and run `bash start-local.sh`.

Open **http://127.0.0.1:8877** after the server reports it is running. This address refers to the computer running the server, not a hosted public site. No ChatGPT account or sign-in is used. Do not open `codex-web/index.html` directly: it needs the backend.

First startup installs all upstream Python dependencies into `.venv`. Later starts reuse that environment. For an existing environment, run `python codex-web/server.py` directly. A different port can be selected with `--port 8878`.

### Native document exporters

Python packages alone do not supply native PDF tools. Install **Pandoc** for LaTeX export and higher-quality Word output, plus **XeLaTeX** for the preferred PDF route. WeasyPrint is bundled as an optional renderer, but the current upstream auto-selection registry only selects Pandoc/XeLaTeX; install that route for original PDF exports.

- Debian/Ubuntu: `sudo apt-get install pandoc texlive-xetex texlive-latex-extra texlive-fonts-recommended lmodern libpango-1.0-0 libpangoft2-1.0-0`
- macOS: install Pandoc and MacTeX (or a sufficiently complete TeX distribution). Follow WeasyPrint's macOS installation guide if using its fallback renderer.
- Windows: install Pandoc and MiKTeX/XeLaTeX and put their executables on PATH. WeasyPrint's Windows native-library setup is separately documented at https://doc.courtbouillon.org/weasyprint/stable/first_steps.html . Restart the launcher after changing PATH.

Native exporters were verified on Linux. Windows/macOS launchers are provided but have **not** been executed on those operating systems. LibreOffice is an optional alternative and was not installed; tested PDF export used Pandoc/XeLaTeX.

## Use the original terminal interface

After setup, activate `.venv` and run `opendraft`. All original CLI commands remain available:

```
opendraft
opendraft --help
opendraft "Your research topic" --level research_paper --style apa
opendraft tldr paper.pdf
opendraft digest paper.pdf --no-audio
opendraft revise ./output "Improve the introduction"
opendraft data list
```

The original `verify` command assumes the engine directory is the working directory. Run it after activation with `cd engine` then `opendraft verify`.

## Browser workflow and feature coverage

| Function | Where to use it | Dependencies / verification |
|---|---|---|
| Research, outline, full draft, citations, quality checks | New paper or original CLI | Installed; requires selected provider key and internet; no live generation verified without keys |
| Research paper, bachelor, master and PhD levels | New paper | Original four levels preserved |
| APA, IEEE, Chicago, MLA, NALT and 12 language choices | New paper | Original options preserved |
| Cover metadata, focus, required sources and context files | New paper → Sources / details | Calls original CLI arguments |
| Exposé only | New paper checkbox | Original outline-only mode; model key required |
| Checkpoint resume | Documents → Resume checkpoint, or original CLI | Select a prior run's checkpoint; browser resumes a copy |
| PDF, DOCX and LaTeX | Documents → upload Markdown → Export | Actual files generated and downloaded in browser verification |
| Summaries and revisions | Documents | Original implementation is Gemini-specific; revision makes a copy |
| Audio digest and script | Documents | Gemini; ElevenLabs additionally required for audio |
| World Bank, Eurostat and OWID datasets | Documents or original CLI | Provider listing verified; remote data calls require internet |
| Run history, logs, cancellation, file downloads | Runs | Added local backend; persistent disk storage |
| Original sample | New paper → Open original sample | Upstream PDF, explicitly labelled; not newly generated |

The CLI retains advanced flags such as dataset date ranges even where the companion has simpler controls.

## Credentials and local storage

Add keys in **Settings** on your own running server. Drafting supports Gemini, Claude or OpenAI. Summary, revision and digest commands remain Gemini-specific upstream. Keys are necessary for real generation; this installation does not include paid API access.

Settings are stored in ignored `codex-web/workspace/settings.local.json` (mode 0600 on POSIX). Jobs, uploads and generated outputs live under that workspace. `OPENDRAFT_WORKSPACE` overrides its location. Existing environment variables are also accepted. To remove a saved key, stop the server and remove the corresponding entry from the local settings file. No keys are committed or returned by the status endpoint.

The server binds to loopback only, validates Host and requires a per-session token on mutations. It is intended for a trusted single-user computer, **not public internet hosting**. Do not reverse-proxy it publicly without authentication, isolation and resource limits. Files are sent to the selected AI provider when the relevant original command uses them. Logs and drafts remain on the local disk. Provider usage may cost money.

## Changes and validation

The only modification to original product code corrects the CLI's provider-key gate: Claude/OpenAI no longer incorrectly require a Google key, and Gemini accepts its documented alias. All original UI text and terminal screens are otherwise preserved. Added browser files, launchers and regression tests are isolated.

- Original suite: **533 passed, 10 skipped, 6 deselected**.
- Original suite plus five new provider-gate tests: **538 passed, 10 skipped, 6 deselected**.
- Excluded integration tests require live services; skipped tests are not claimed as passed.
- Browser regression: genuine sample download, document upload, PDF/DOCX/LaTeX export, CLI help, dataset listing, saved history, mobile layout and access checks. See `verification/browser-results.json` for the result.
- `opendraft verify`: Python, dependencies, PDF engines and project structure pass. API-key check fails as expected because no key is configured.

Run engine tests with `python -m pip install -e 'engine[pdf,dev]' -r requirements.txt` then `python -m pytest -q`. For browser verification install Playwright/Chromium, start a server with an empty workspace and no keys, then run `python codex-web/test_browser.py`. Set `CHROMIUM_PATH` if it is not `/usr/bin/chromium`.

This is a working local installation, not evidence that a complete AI-written research paper or audio digest has been produced here. Those checks remain pending provider configuration.

## Licence

OpenDraft is MIT, copyright **2025 SCAILE Technologies GmbH**. The original `LICENSE` is preserved. Companion additions are distributed under the same MIT terms. Dependency licences remain with their upstream packages. No OpenPaper proprietary interface or hosted source has been copied.
