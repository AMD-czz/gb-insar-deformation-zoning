"""Generate or verify the release manifest (Python standard library only).

Run from any directory:
  python tools/manifest.py generate
  python tools/manifest.py verify

FILE_MANIFEST.csv excludes itself; Git provides commit integrity for that file.
Generated outputs, environments, Git internals and Python caches are excluded.
Verification checks raw bytes; do not normalize before verification.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.git', '__pycache__', '.venv', 'outputs', '.pytest_cache'}

def release_files(root):
    return sorted((p for p in root.rglob('*') if p.is_file()
        and not (set(p.relative_to(root).parts[:-1]) & EXCLUDED_DIRS)
        and p.name != 'FILE_MANIFEST.csv' and p.suffix not in {'.pyc', '.pyo'}),
        key=lambda p: p.relative_to(root).as_posix())

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def generate(root):
    files = release_files(root)
    with (root / 'FILE_MANIFEST.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['relative_path', 'bytes', 'sha256'])
        for p in files:
            w.writerow([p.relative_to(root).as_posix(), p.stat().st_size, sha256(p)])
    print(f'Generated manifest: {len(files)} files (manifest excludes itself).')

def verify(root):
    with (root / 'FILE_MANIFEST.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    errors = []
    paths = [r['relative_path'] for r in rows]
    if len(paths) != len(set(paths)):
        errors.append('Duplicate manifest paths')
    for r in rows:
        p = (root / r['relative_path']).resolve()
        if not p.is_relative_to(root.resolve()):
            errors.append('Unsafe manifest path'); continue
        if not p.is_file():
            errors.append('Missing: ' + r['relative_path']); continue
        if p.stat().st_size != int(r['bytes']) or sha256(p) != r['sha256']:
            errors.append('Mismatch: ' + r['relative_path'])
    actual = {p.relative_to(root).as_posix() for p in release_files(root)}
    for p in sorted(actual - set(paths)):
        errors.append('Unlisted: ' + p)
    if errors:
        print('\n'.join(errors)); return 1
    print(f'PASS: all {len(rows)} listed files match; no unlisted release files.')
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['generate', 'verify'])
    args = parser.parse_args()
    if args.mode == 'generate': generate(ROOT)
    else: sys.exit(verify(ROOT))

if __name__ == '__main__': main()
