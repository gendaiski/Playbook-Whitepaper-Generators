# Playbook & Whitepaper Generators

## WhitePaperBuilder

[Open the verified live original interface](https://white-paper-builder.aelgendy673996.chatgpt.site/) — no ChatGPT sign-in required.

[Source and setup documentation](sources/whitepaperbuilder/systems/whitepaperbuilder/README.md) · [Original standalone HTML](sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/index.html) · [Original tests](sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/Tests)

This is a complete source snapshot of the installed WhitePaperBuilder package from `gendaiski/Sandbox-2`, branch `codex/whitepaperbuilder-install`. Its original interface supports white papers, citations, charts, timelines, project JSON and browser PDF printing. It runs in the browser; no server backend or API key is required.

Download/clone the repository, then open `sources/whitepaperbuilder/systems/whitepaperbuilder/upstream/index.html`. GitHub itself displays HTML code rather than executing it.

Original MIT, Paged.js and IBM Plex font notices remain inside the package. Source provenance and hashes are in `provenance/whitepaperbuilder.json`; run `python3 tools/verify_integrity.py` to verify the copy.

The destination was empty: `codex/collection-base` is the empty review base; `codex/import-generators` holds the import. A pull request records the changes. No auto-merge or deployment is configured.

No separate playbook product was named for import in this request; only the selected white-paper generator is included. All other selected systems belong in Post-Desk-Repo.
