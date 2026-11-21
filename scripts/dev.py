#!/usr/bin/env python
"""
TourPLUS — Concurrent Full-Stack Development Server Runner.
Runs both the Django backend (port 8000) and Next.js frontend (port 3000) in one go.
Handles graceful shutdown of both child processes upon Ctrl+C.
"""

import os
import sys
import shutil
import signal
import subprocess
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

# Determine Python executable
if sys.platform == 'win32':
    venv_python = os.path.join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe')
else:
    venv_python = os.path.join(BACKEND_DIR, '.venv', 'bin', 'python')

python_exe = venv_python if os.path.exists(venv_python) else sys.executable

# Determine pnpm / npm executable
pnpm_path = shutil.which('pnpm') or shutil.which('pnpm.cmd')
npm_path = shutil.which('npm') or shutil.which('npm.cmd')
pkg_manager = pnpm_path if pnpm_path else npm_path


def main():
    print("=" * 65)
    print("  TourPLUS — Starting Full-Stack Development Environment")
    print("=" * 65)
    print(f"  Root Directory : {ROOT_DIR}")
    print(f"  Python Path    : {python_exe}")
    print(f"  Package Runner : {pkg_manager}")
    print("-" * 65)

    if not pkg_manager:
        print("ERROR: Neither 'pnpm' nor 'npm' was found on your system PATH.")
        sys.exit(1)

    # 1. Quick migration check
    print("\n[INIT] Running database migrations check...")
    manage_py = os.path.join(BACKEND_DIR, 'manage.py')
    try:
        subprocess.run([python_exe, manage_py, "migrate", "--noinput"], cwd=BACKEND_DIR, check=True)
    except Exception as e:
        print(f"[WARN] Migration check returned: {e}")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    processes = []

    # 2. Launch Django Backend
    print("[START] Launching Django Backend at http://localhost:8000/api/v1/ ...")
    backend_cmd = [python_exe, manage_py, "runserver", "0.0.0.0:8000"]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=BACKEND_DIR,
        env=env
    )
    processes.append(("Backend", backend_proc))

    # Give backend a second to bind
    time.sleep(1)

    # 3. Launch Next.js Frontend
    print("[START] Launching Next.js Frontend at http://localhost:3000/ ...\n")
    frontend_cmd = [pkg_manager, "run", "dev"]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        shell=(sys.platform == 'win32')
    )
    processes.append(("Frontend", frontend_proc))

    print("-" * 65)
    print("  Both servers are running concurrently!")
    print("  -> Frontend: http://localhost:3000/")
    print("  -> Backend : http://localhost:8000/api/v1/")
    print("  -> Admin   : http://localhost:8000/admin/")
    print("  Press Ctrl+C to terminate both servers.")
    print("-" * 65 + "\n")

    def cleanup(signum=None, frame=None):
        print("\n\n[STOP] Shutting down TourPLUS services...")
        for name, proc in processes:
            try:
                print(f"[STOP] Terminating {name} (PID {proc.pid})...")
                if sys.platform == 'win32':
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    proc.terminate()
            except Exception:
                pass
        print("[STOP] All services stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            # Check if any process terminated prematurely
            for name, proc in processes:
                ret = proc.poll()
                if ret is not None:
                    print(f"\n[ALERT] {name} process exited with code {ret}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == '__main__':
    main()
