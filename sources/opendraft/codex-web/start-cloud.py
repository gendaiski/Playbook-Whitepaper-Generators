"""Start the protected companion in a cloud VM. Retains its personal access key."""
import os
import secrets
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
hostname = os.environ.get('OPENDRAFT_PUBLIC_HOST', '')
if not hostname or '/' in hostname or any(c.isspace() for c in hostname):
    raise SystemExit('Set OPENDRAFT_PUBLIC_HOST to the exact HTTPS hostname first.')
workspace = Path(os.environ.get('OPENDRAFT_WORKSPACE', root / 'codex-web/workspace')).resolve()
workspace.mkdir(parents=True, exist_ok=True)
access = Path(os.environ.get('OPENDRAFT_ACCESS_FILE', workspace / '.preview-access'))
if not access.exists():
    fd = os.open(access, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w') as handle:
        handle.write(secrets.token_urlsafe(32))
env = os.environ.copy()
env.update(OPENDRAFT_ACCESS_TOKEN=access.read_text().strip(), OPENDRAFT_BIND_HOST='0.0.0.0', OPENDRAFT_WORKSPACE=str(workspace))
os.execve(sys.executable, [sys.executable, str(root / 'codex-web/server.py'), '--port', os.environ.get('PORT', '8879')], env)
