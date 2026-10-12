#!/usr/bin/env python
"""
AgriSmart Unified Platform - One-Command Application Runner
=============================================================
Entry point to initialize, configure, and launch the complete
precision agriculture, crop advisory, and marketplace application.

Usage:
    python app.py
"""

import os
import sys
import time
import socket
import signal
import threading
import webbrowser
from pathlib import Path

# Configure utf-8 stdout/stderr for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Project Roots
ROOT_DIR = Path(__file__).resolve().parent
AGRISMART_DIR = ROOT_DIR / "agrismart"
INNER_PROJECT_DIR = ROOT_DIR / "Codebind technologies project"

# Ensure AGRISMART_DIR is at the top of sys.path so 'import app' resolves to agrismart/app
sys.path = [str(AGRISMART_DIR), str(ROOT_DIR), str(INNER_PROJECT_DIR)] + [p for p in sys.path if p not in (str(AGRISMART_DIR), str(ROOT_DIR), str(INNER_PROJECT_DIR))]

# Ensure working directory is agrismart for relative database & template assets
os.chdir(str(AGRISMART_DIR))


def find_venv_python():
    """Locates virtual environment Python interpreter if available."""
    candidates = [
        AGRISMART_DIR / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python"),
        ROOT_DIR / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python"),
        INNER_PROJECT_DIR / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def verify_dependencies():
    """Checks for required Python dependencies and re-spawns with venv if needed."""
    required = [
        ("flask", "Flask"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("flask_login", "Flask-Login"),
        ("dotenv", "python-dotenv"),
        ("pandas", "pandas"),
        ("sklearn", "scikit-learn"),
        ("joblib", "joblib"),
        ("requests", "requests"),
        ("reportlab", "reportlab"),
    ]

    missing = []
    for module_name, pkg_name in required:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        # Check if a project virtual environment has the packages
        venv_py = find_venv_python()
        if venv_py and str(venv_py) != sys.executable:
            print(f"[*] Detected project virtual environment at: {venv_py}")
            print("[*] Re-spawning runner with virtual environment interpreter...\n")
            # Re-spawn using the virtual environment interpreter
            import subprocess
            res = subprocess.call([str(venv_py), str(ROOT_DIR / "app.py")] + sys.argv[1:])
            sys.exit(res)

        print("\n" + "=" * 65)
        print("  [!] MISSING DEPENDENCIES DETECTED")
        print("=" * 65)
        print("The following required packages are not installed in the active Python environment:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nPlease run the following command to install all dependencies:")
        print(f"\n   pip install -r \"{ROOT_DIR / 'requirements.txt'}\"\n")
        print("=" * 65 + "\n")
        sys.exit(1)


# Verify dependencies before continuing
verify_dependencies()

# Load Environment Variables
try:
    from dotenv import load_dotenv
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        example_env = ROOT_DIR / ".env.example"
        if example_env.exists():
            import shutil
            shutil.copy(example_env, env_file)
            print("[*] Created .env configuration file from .env.example")
    load_dotenv(str(env_file))
except Exception as e:
    print(f"[!] Notice: Could not load .env file: {e}")


def is_port_in_use(port, host="127.0.0.1"):
    """Check if the specified network port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


def wait_and_open_browser(url, timeout=15):
    """Polls the local server and opens the browser once ready."""
    start_time = time.time()
    opened = False
    while time.time() - start_time < timeout:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'AgriSmart-HealthCheck'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status in (200, 302):
                    time.sleep(0.5)
                    webbrowser.open(url)
                    opened = True
                    break
        except Exception:
            time.sleep(0.4)
    if not opened:
        # Fallback open after timeout
        try:
            webbrowser.open(url)
        except Exception:
            pass


def print_banner(host, port):
    """Displays styled startup information in terminal."""
    url = f"http://localhost:{port}" if host in ("0.0.0.0", "127.0.0.1") else f"http://{host}:{port}"
    print("\n" + "=" * 70)
    print("🌾  AGRISMART - UNIFIED PRECISION AGRICULTURE & ADVISORY SYSTEM")
    print("=" * 70)
    print(f"  * Localhost Web URL     :  {url}")
    print(f"  * 730+ Location Engine   :  {url}/predict")
    print(f"  * Farmer Dashboard       :  {url}/dashboard/")
    print(f"  * Agro-Marketplace       :  {url}/marketplace/")
    print("-" * 70)
    print("  * Demo Farmer Login      :  farmer_ravi  /  password123")
    print("  * Demo Admin Login       :  admin        /  admin123")
    print("-" * 70)
    print("  * Press Ctrl+C in this terminal anytime to stop the server.")
    print("=" * 70 + "\n")


def initialize_database(app, db):
    """Ensures database tables exist and seeds initial data if database is empty."""
    with app.app_context():
        # Ensure database instance directory exists
        instance_dir = AGRISMART_DIR / "instance"
        instance_dir.mkdir(parents=True, exist_ok=True)

        # Create all tables safely (does not overwrite existing data)
        db.create_all()

        # Check if users or products need initial seeding
        try:
            from app.models import User, Product
            user_count = User.query.count()
            product_count = Product.query.count()

            if user_count == 0 or product_count == 0:
                print("[*] Database is empty. Seeding initial farmer demo accounts and products...")
                from seed import seed_database
                seed_database()
            else:
                print(f"[✓] Database verified: {user_count} registered users, {product_count} marketplace products.")
        except Exception as e:
            print(f"[!] Notice during database verification: {e}")


def main():
    """Main execution workflow."""
    # Server configuration
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port_str = os.environ.get("SERVER_PORT", "5000")
    try:
        port = int(port_str)
    except ValueError:
        port = 5000

    # Check for port collisions
    if is_port_in_use(port):
        print(f"[!] Warning: Port {port} is already in use by another process.")
        print(f"[!] You can already access the running server at http://localhost:{port}")
        # Try alternate port if needed
        alt_port = port + 1
        print(f"[*] Checking alternate port {alt_port}...")
        if not is_port_in_use(alt_port):
            port = alt_port
            print(f"[*] Bound server to alternate port: {port}")
        else:
            print(f"[!] Please close any conflicting processes on port {port} or {alt_port} and rerun.")
            sys.exit(1)

    # Initialize Flask App
    try:
        from app import create_app, db
        flask_env = os.environ.get("FLASK_ENV", "development")
        app = create_app(flask_env)
    except Exception as e:
        print(f"\n[!] Fatal Error during application factory initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Database setup & verification
    initialize_database(app, db)

    # Display Startup Banner
    print_banner(host, port)

    # Automatic browser launch thread
    auto_open = os.environ.get("AUTO_OPEN_BROWSER", "true").lower() in ("true", "1", "yes")
    if auto_open:
        browser_thread = threading.Thread(
            target=wait_and_open_browser,
            args=(f"http://localhost:{port}/predict",),
            daemon=True
        )
        browser_thread.start()

    # Graceful shutdown handler
    def handle_shutdown(signum, frame):
        print("\n\n[*] Shutting down AgriSmart gracefully. Goodbye!\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_shutdown)

    # Start Flask Web Server
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=False
    )


if __name__ == "__main__":
    main()
