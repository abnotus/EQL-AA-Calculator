#!/usr/bin/env python3
"""
Runs every tests/test_*.py in one pass and reports a summary - the same
loop this project's own sessions have been hand-typing at a shell prompt,
committed for real so nobody has to retype or remember it.

    python tests/run_all.py

Starts its own `python -m http.server` for the browser tests (killed again
once the run finishes, whether or not everything passed) rather than
assuming one is already running - AACALC_TEST_PORT (default 8743) picks
the port, matching every individual test file's own default. Each test
runs as its own subprocess, under PER_TEST_TIMEOUT_SECONDS, so one stalled
test can't hang the whole run - a timeout is reported and counted as a
failure, same as a normal assertion failure, and the run continues with
whatever's left.

Not wired into CI (see the project's own notes on why, for now) - this is
purely the manual-run convenience the review that prompted it asked for.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
PORT = os.environ.get("AACALC_TEST_PORT", "8743")
BASE_URL = f"http://localhost:{PORT}/index.html"
PER_TEST_TIMEOUT_SECONDS = 90
SERVER_READY_TIMEOUT_SECONDS = 10


def port_is_taken():
    # A successful connect means SOMETHING is already listening there -
    # distinct from "our own server, just not ready yet" (that's a refused
    # connection, not an accepted one). Checked before spawning our own
    # server specifically so a pre-existing occupant (a leftover process,
    # a stale checkout's own server, anything) is caught as a loud failure
    # up front, rather than the readiness poll below mistaking its answer
    # for proof our subprocess is the one serving.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", int(PORT))) == 0


def start_server():
    if port_is_taken():
        raise RuntimeError(
            f"port {PORT} is already in use by something else - stop it first, "
            f"or set AACALC_TEST_PORT to a different port and retry. Proceeding "
            f"anyway would risk testing whatever's already answering there "
            f"instead of this checkout's own build."
        )
    # http.server logs every request it handles to stderr, for as long as
    # it runs - not just at startup. stderr=subprocess.PIPE with nothing
    # ever draining it (an earlier version of this function did exactly
    # that, to capture a startup crash) fills the pipe's fixed OS buffer
    # after enough requests; once full, the single-threaded server blocks
    # on its own next log write and stops answering, which looks exactly
    # like a hung/crashed server from the outside. A real file has no such
    # backpressure - the OS just keeps appending - so this redirects there
    # instead, for the server's entire lifetime, and only ever reads the
    # file back on an actual startup failure (main() deletes it afterward
    # either way).
    log_file = tempfile.NamedTemporaryFile(prefix="aacalc_test_server_", suffix=".log", delete=False)
    log_path = log_file.name
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", PORT],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=log_file,
    )
    # The child's own handle to the file (duplicated at process-creation
    # time) is independent of this one - closing the parent's copy here
    # doesn't affect the child's ability to keep writing to it.
    log_file.close()

    def fail_startup(message):
        try:
            log_text = Path(log_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            log_text = "(couldn't read server log)"
        try:
            os.unlink(log_path)
        except OSError:
            pass
        raise RuntimeError(f"{message}\nserver log:\n{log_text}")

    deadline = time.time() + SERVER_READY_TIMEOUT_SECONDS
    while time.time() < deadline:
        # Checked ahead of the HTTP probe on every iteration - if the
        # subprocess has already exited, no HTTP response that follows can
        # possibly be coming from it, no matter what it looks like.
        if proc.poll() is not None:
            fail_startup(f"local test server process exited immediately (exit {proc.returncode})")
        try:
            urllib.request.urlopen(BASE_URL, timeout=1)
            return proc, log_path
        except Exception:
            time.sleep(0.2)
    proc.terminate()
    fail_startup(f"local test server never became ready on port {PORT}")


def run_one(test_path):
    env = dict(os.environ)
    env["AACALC_TEST_PORT"] = PORT
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=PER_TEST_TIMEOUT_SECONDS,
        )
        status = "pass" if result.returncode == 0 else "fail"
        return (status, result.stdout, result.stderr)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return ("timeout", out, err)


def main():
    test_files = sorted(TESTS_DIR.glob("test_*.py"))
    if not test_files:
        print("No tests/test_*.py files found.")
        return 1

    print(f"Discovered {len(test_files)} test file(s). Starting local server on port {PORT}...")
    server, log_path = start_server()
    try:
        results = []
        for i, path in enumerate(test_files, 1):
            name = path.name
            print(f"[{i}/{len(test_files)}] {name} ...", end=" ", flush=True)
            status, out, err = run_one(path)
            results.append((name, status, out, err))
            print(status.upper())
            if status != "pass":
                tail = "\n".join((out + err).strip().splitlines()[-25:])
                print(f"  --- last output from {name} ---")
                for line in tail.splitlines():
                    print(f"  {line}")
                print(f"  --- end {name} ---")
        return summarize(results)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        try:
            os.unlink(log_path)
        except OSError:
            pass


def summarize(results):
    passed = [r for r in results if r[1] == "pass"]
    failed = [r for r in results if r[1] == "fail"]
    timed_out = [r for r in results if r[1] == "timeout"]
    print()
    print(f"{len(passed)}/{len(results)} passed.")
    if failed:
        print(f"FAILED ({len(failed)}): " + ", ".join(name for name, *_ in failed))
    if timed_out:
        print(f"TIMED OUT ({len(timed_out)}, over {PER_TEST_TIMEOUT_SECONDS}s): " + ", ".join(name for name, *_ in timed_out))
    if not failed and not timed_out:
        print("ALL PASS")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
