import os, sys, subprocess

def test_cli_runs():
    r = subprocess.run(
        [sys.executable, "cli.py", "你好"],
        capture_output=True, text=True, timeout=15,
        env={**os.environ, "HY3_MOCK": "true"},
    )
    assert r.returncode == 0
    assert r.stdout.strip()
