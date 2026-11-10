# Playbook & Whitepaper Generators

## WhitePaperBuilder

[Open the verified live original interface](https://white-paper-builder.aelgendy673996.chatgpt.site/) — no ChatGPT sign-in required.

[Source and setup documentation](sources/whitepaperbuilder/systems/whitepaperbuilder/README.md) · [Original standalone HTML](sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/index.html) · [Original tests](sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/Tests)

This is a complete source snapshot of the installed WhitePaperBuilder package from `gendaiski/Sandbox-2`, branch `codex/whitepaperbuilder-install`. Its original interface supports white papers, citations, charts, timelines, project JSON and browser PDF printing. It runs in the browser; no server backend or API key is required.

Download/clone the repository, then open `sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/index.html`. GitHub itself displays HTML code rather than executing it.

Original MIT, Paged.js and IBM Plex font notices remain inside the package. Source provenance and hashes are in `provenance/whitepaperbuilder.json`; run `python3 tools/verify_integrity.py` to verify the copy.

The destination was empty: `codex/collection-base` is the empty review base; `codex/import-generators` holds the import. A pull request records the changes. No auto-merge or deployment is configured.

No separate playbook product was named for import. Other selected social/video/design systems belong in Post-Desk-Repo.


## OpenDraft 1.8.1

[Full source and original README](sources/opendraft/README.md) · [Installation and feature coverage](sources/opendraft/INSTALLATION-CODEX.md) · [Browser verification](sources/opendraft/verification/browser-results.json)

Installed with its complete original Python engine and terminal CLI. The repository has no original web frontend; `codex-web/` adds a clearly labelled local browser companion connected to the real engine. Original OpenPaper hosted screens are not part of this source.

Run `Start-Windows.cmd` on Windows or `bash start-local.sh` on macOS/Linux from `sources/opendraft`. After startup, open `http://127.0.0.1:8877` on the same computer. Native PDF tools need separate installation as documented. There is no ChatGPT sign-in and no public deployment.

Verified on Linux: 538 engine/provider tests passed, 10 skipped, six integration tests deselected; real PDF, DOCX and LaTeX generation/downloads, sample PDF, uploads, original CLI help, provider listing and browser history passed. No AI key is included: live drafting, summaries, revision and audio still require your provider configuration. Windows/macOS launchers are supplied but not OS-tested.

MIT notices preserved. Provenance, exact upstream revision and the three changed upstream files are recorded in `provenance/opendraft.json`. This addition uses its own `codex/opendraft-install` branch and PR based on the existing import branch; nothing is merged automatically.

Personal HTTPS access is prepared on `codex/opendraft-cloud-access`; public exposure awaits explicit Cloudflare approval. See [preview status and access design](sources/opendraft/CLOUD-PREVIEW.md). No public live URL is claimed yet.
