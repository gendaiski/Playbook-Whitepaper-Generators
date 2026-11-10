"""Verify the archived source files without installing or executing imported apps."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'SOURCE-FILES.json').read_text())
errors=[]
for row in manifest:
 p=root/row['path']
 if not p.is_file():errors.append(row['path']+': missing');continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append(row['path']+': checksum mismatch')
 if p.stat().st_size!=row['bytes']:errors.append(row['path']+': size mismatch')
if errors:
 print('\n'.join(errors));sys.exit(1)
print(f"PASS: {len(manifest)} imported files match their recorded SHA-256 hashes.")
