import subprocess
import glob
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(root)

# find test files: tests/*.py and root-level test_*.py
files = glob.glob('tests/**/*.py', recursive=True) + glob.glob('test_*.py')
files = sorted(set(files))

results = []
for f in files:
    print(f"Running {f}...")
    cmd = [os.path.join('.venv','Scripts','python.exe'), '-m', 'pytest', f, '-q', '--disable-warnings']
    try:
        proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=600)
        out = proc.stdout + proc.stderr
        passed = proc.returncode == 0
    except subprocess.TimeoutExpired:
        out = 'Timeout'
        passed = False
    results.append((f, passed, out[:2000]))
    print(f"-> {'PASS' if passed else 'FAIL'}\n")

print('\nSummary:')
for f, passed, out in results:
    print(f"{f}: {'PASS' if passed else 'FAIL'}")

failed = [r for r in results if not r[1]]
if failed:
    print('\nFailed files details (truncated):')
    for f, passed, out in failed:
        print('\n---', f, '---')
        print(out)

# exit code
import sys
sys.exit(0 if not failed else 1)
