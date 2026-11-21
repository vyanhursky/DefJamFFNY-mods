"""Data-only fighter inventory checks from a pinned released game source.

No game dump, lifted code or executable is required. Verification jobs check out
this exact reviewed source separately; the protected signer never calls it.
Run its existing validator in an isolated Python process, never from a pack.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_COMMIT = '2496bd3429a854a842701070cbeb5a54c5e3f445'  # v1.2.1
SOURCE_ENV = 'DEFJAM_FIGHTER_VALIDATOR_SOURCE'

PROGRAM = '''
import json, sys
sys.path.insert(0, sys.argv[1])
from fighter_packages import receipt
print(json.dumps(receipt(sys.argv[2]), allow_nan=False))
'''


def runtime_source():
    source = Path(os.environ.get(SOURCE_ENV, ROOT / '.fighter-validator')).resolve()
    if not (source / 'setup/fighter_packages.py').is_file():
        raise ValueError('Fighter verification needs the pinned v1.2.1 source checkout; see docs/fighter-catalogue.md')
    # This path is configured by the verifier/owner, never supplied by the ZIP.
    # Reject a different checkout or modified compiler/configuration before imports.
    head = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'],
                          capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    if head != RUNTIME_COMMIT:
        raise ValueError('Fighter validator source does not match the pinned release commit')
    clean = subprocess.run(['git', '-C', str(source), 'diff', '--quiet', 'HEAD', '--', 'setup', 'config'],
                           capture_output=True, timeout=30)
    if clean.returncode:
        raise ValueError('Fighter validator source/configuration has local changes')
    tracked = set(subprocess.run(['git', '-C', str(source), 'ls-files', '--', 'setup'],
                                 capture_output=True, text=True, timeout=30, check=True).stdout.splitlines())
    for path in (source / 'setup').rglob('*.py'):
        if path.relative_to(source).as_posix() not in tracked:
            raise ValueError('Unexpected Python source in the fighter validator checkout')
    return source


def validate_fighter(folder):
    source = runtime_source()
    # -I excludes inherited PYTHONPATH/user-site and the working directory from
    # imports. -B keeps the reviewed source tree immutable. The asset folder is
    # only a data argument: it never joins sys.path and supplies no commands.
    result = subprocess.run([sys.executable, '-I', '-B', '-c', PROGRAM,
                             str(source / 'setup'), str(Path(folder).resolve())],
                            cwd=source, capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError('Released fighter inventory validation refused the pack: ' + result.stderr[-3000:])
    try:
        value = json.loads(result.stdout)
    except ValueError as error:
        raise ValueError('Invalid fighter validation receipt') from error
    if (not isinstance(value, dict) or value.get('category') != 'fighters'
            or value.get('capabilities') != ['fighters-v1']):
        raise ValueError('Unexpected fighter validation receipt')
    return value
