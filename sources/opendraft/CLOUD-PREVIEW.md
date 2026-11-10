# Personal HTTPS preview

This addition prepares the installed OpenDraft engine for a personal HTTPS preview without a ChatGPT account. It does not replace the original engine or terminal interface.

## Current status — 2026-11-10

- Railway creation was rejected: `Free plan resource provision limit exceeded`.
- Render's connected workspace-list tool returned `Unknown tool`.
- A separate localhost workspace and access-protected backend have been prepared and tested.
- **No public tunnel has been started.** Automatic approval review rejected that operation because the user had not explicitly approved exposing this uploads/provider-settings backend through Cloudflare. Explicit approval is pending.

## Access design

Set `OPENDRAFT_ACCESS_TOKEN` to a cryptographically random value of at least 32 characters before starting `codex-web/server.py`. With this setting, the root page accepts a personal access fragment and exchanges it for a Secure, HttpOnly, SameSite=Strict cookie. All application pages, APIs and downloads require this cookie. The health endpoint reports only `{"ok":true}`. The fragment is removed from browser history before the exchange. Mutations still require the existing CSRF token.

Only share the personal link with its intended recipient. Anyone holding it can use the single-user workspace. Do not commit the token, add it to deployment logs or publish it in repository documentation. Provider keys must be entered by the owner in Settings, never hardcoded.

The server continues to bind to loopback and enforce the expected Host header. An approved tunnel must forward that expected Host value. Without `OPENDRAFT_ACCESS_TOKEN`, existing local-only behavior is retained; do not expose that mode publicly.

Use the virtual environment's full Python path both as the executable and as argv[0] when launching programmatically. A short argv[0] can resolve the wrong Python interpreter for child processes.

## Limits

A quick tunnel is temporary, depends on this execution environment staying alive and does not provide permanent storage or hosting. Files and provider settings are held on this running server; download outputs you want to retain. Public HTTPS behavior must be checked after an approved tunnel starts. Local browser checks do not establish that a public URL is live.

## Tests

Run `python codex-web/test_cloud_access.py` for seven offline access-control tests. For the browser regression use an empty test workspace and set `OPENDRAFT_TEST_URL`, `OPENDRAFT_TEST_ACCESS_FILE` and `OPENDRAFT_TEST_REPORTS` as appropriate. The access file is outside the repository and contains a temporary test access token.
