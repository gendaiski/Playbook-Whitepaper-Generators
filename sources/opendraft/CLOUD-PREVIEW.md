# Personal HTTPS preview

This addition prepares the installed OpenDraft engine for a personal HTTPS preview without a ChatGPT account. It does not replace the original engine or terminal interface.

## Current status — 2026-11-10

- Railway creation was rejected: `Free plan resource provision limit exceeded`.
- Render's connected workspace-list tool returned `Unknown tool`.
- A separate localhost workspace and access-protected backend have been prepared and tested.
- The user explicitly approved the Cloudflare tunnel. Cloudflare setup then failed with connection refusal and an HTTP 403 response. No tunnel was created.
- OpenDraft is now installed in a Vercel Sandbox with a public HTTPS route and the personal-link access gate. This uses the connected Gendaiski Hobby plan, whose sessions are limited to 45 minutes.
- Current public route: `https://sb-whjcxg0lkwsb.vercel.run`. The access fragment is shared only in the private chat, never in this repository.
- Current session is scheduled to stop at **2026-11-10 19:51:50 UTC**. This is a temporary preview, not permanent hosting.

## Access design

Set `OPENDRAFT_ACCESS_TOKEN` to a cryptographically random value of at least 32 characters before starting `codex-web/server.py`. With this setting, the root page accepts a personal access fragment and exchanges it for a Secure, HttpOnly, SameSite=Strict cookie. All application pages, APIs and downloads require this cookie. The health endpoint reports only `{"ok":true}`. The fragment is removed from browser history before the exchange. Mutations still require the existing CSRF token.

Only share the personal link with its intended recipient. Anyone holding it can use the single-user workspace. Do not commit the token, add it to deployment logs or publish it in repository documentation. Provider keys must be entered by the owner in Settings, never hardcoded.

The server defaults to loopback. Remote binding requires both a personal access token and an exact `OPENDRAFT_PUBLIC_HOST`; only that hostname and localhost are accepted. `codex-web/start-cloud.py` prepares the access key and starts this protected mode. Without `OPENDRAFT_ACCESS_TOKEN`, existing local-only behavior is retained; remote binding is refused.

Use the virtual environment's full Python path both as the executable and as argv[0] when launching programmatically. A short argv[0] can resolve the wrong Python interpreter for child processes.

## Limits

A quick tunnel is temporary, depends on this execution environment staying alive and does not provide permanent storage or hosting. Files and provider settings are held on this running server; download outputs you want to retain. Public HTTPS behavior was verified in Chromium against the Vercel route, including protected entry, real exports and mobile layout. See `verification/public-preview-results.json`. AI generation remains unverified without provider keys.

## Tests

Run `python codex-web/test_cloud_access.py` for seven offline access-control tests. For the browser regression use an empty test workspace and set `OPENDRAFT_TEST_URL`, `OPENDRAFT_TEST_ACCESS_FILE` and `OPENDRAFT_TEST_REPORTS` as appropriate. The access file is outside the repository and contains a temporary test access token.


## Resume the Vercel preview

Team: `team_6EOWs9KFetQQNpHUN2XlEuXK`; project: `prj_KZ5vWdlqhqszaIzAMEKuTFvU0Map`; named sandbox: `opendraft-ipad`. Installed source is `/vercel/Playbook-Whitepaper-Generators/sources/opendraft`.

Retrieve/resume the named sandbox through Vercel, inspect its current routes, and restart the server (processes do not survive snapshots). Run `.venv/bin/python codex-web/start-cloud.py` from the source directory with:

- `OPENDRAFT_PUBLIC_HOST`: the current HTTPS route hostname
- `OPENDRAFT_ACCESS_FILE=/vercel/opendraft-personal-access`
- `OPENDRAFT_WORKSPACE=/vercel/opendraft-workspace`
- `PORT=8879`

The token is an owner-only file in the VM, outside Git. Keep its contents out of logs and commits. The launch script retains it rather than rotating it. Re-share the current route with its access fragment privately. Recheck `/health`, protected access and an export before calling the resumed preview live.

Installation uses Python 3.12 via uv, all original `engine[pdf]` and root requirements, Pandoc, Pango, XeLaTeX, TeX extra/recommended packages and `lmodern`. Upstream's PDF registry currently selects Pandoc/XeLaTeX only despite mentioning a WeasyPrint fallback, so the TeX packages are necessary for the original export function.
