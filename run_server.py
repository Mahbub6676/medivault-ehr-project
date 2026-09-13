#!/usr/bin/env python
"""Convenience launcher used by the online sandbox preview.

It makes sure Django is installed, applies migrations, seeds the demo data on a
fresh database and then starts the Django development server on $PORT.

For normal local development just use the standard Django commands instead:

    python manage.py migrate
    python manage.py seed_data
    python manage.py runserver
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = os.environ.get("PORT", "3000")


def ensure_django():
    try:
        import django  # noqa: F401
        return
    except ImportError:
        pass
    for args in (
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q",
         "-r", "requirements.txt"],
        [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
    ):
        if subprocess.call(args, cwd=BASE_DIR) == 0:
            return
    sys.exit("Could not install Django. Run: pip install -r requirements.txt")


def manage(*args):
    return subprocess.call([sys.executable, "manage.py", *args], cwd=BASE_DIR)


def main():
    ensure_django()
    manage("migrate", "--noinput")
    manage("seed_data")
    if "--build-only" in sys.argv:
        print("MediVault EHR: database ready (build step finished).")
        return
    print(f"MediVault EHR: starting Django server on 0.0.0.0:{PORT}", flush=True)
    os.execv(sys.executable, [sys.executable, "manage.py", "runserver",
                              f"0.0.0.0:{PORT}", "--noreload"])


if __name__ == "__main__":
    main()
