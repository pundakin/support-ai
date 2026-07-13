"""
Script to check basic environment readiness.
Run: python scripts/check_env.py

Checks:
- Presence of virtual environment
- Installation of key packages
- Loading configuration from .env
"""
import sys
from pathlib import Path

# Adding the project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_venv():
    """Check activation of the virtual environment."""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment is not activated")
        print("   Activate: source .venv/bin/activate")
        return False
    print("✅ Virtual environment: active")
    return True


def check_packages():
    """Check installation of key packages."""
    required = ["fastapi", "langgraph", "sqlalchemy", "pydantic"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"❌ Packages not installed: {missing}")
        print("   Run: pip install -r requirements.txt")
        return False

    print(f"✅ Dependencies: installed ({len(required)} packages)")
    return True


def check_config():
    """Check loading of configuration."""
    try:
        from app.config import get_settings
        settings = get_settings()

        # Check required fields
        if not settings.SECRET_KEY or settings.SECRET_KEY == "change-me-in-prod":
            print("⚠️  SECRET_KEY is not configured (using default)")

        print(f"✅ Configuration: loaded (mode: {settings.APP_ENV})")
        return True

    except Exception as e:
        print(f"❌ Configuration: loading error — {e}")
        return False


def main():
    print("🔍 Checking environment...\n")

    checks = [
        check_venv(),
        check_packages(),
        check_config(),
    ]

    print()
    if all(checks):
        print("🎉 Environment is ready for development!")
        return 0
    else:
        print("⚠️  Fix warnings before continuing")
        return 1


if __name__ == "__main__":
    sys.exit(main())