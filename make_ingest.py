#!/usr/bin/env python3
"""
Digest generation script using gitingest.
Development utility for creating code digests for Atlas-Template.
"""

import importlib.util
import logging
import shutil
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def _resolve_gitingest_command():
    cli_path = shutil.which("gitingest")
    if cli_path:
        return [cli_path]

    if importlib.util.find_spec("gitingest.cli") is not None:
        return [sys.executable, "-m", "gitingest.cli"]

    return None


def generate_digest_cli(
    source, output_file="digest.txt", exclude_exts=None, is_frontend=False
):
    base_cmd = _resolve_gitingest_command()
    if not base_cmd:
        log.error(
            "gitingest is not available. Install it with "
            "'python -m pip install gitingest' or add the gitingest executable to PATH."
        )
        return

    cmd = base_cmd + [source, "-o", output_file]

    # Frontend-specific exclusions when processing frontend folder
    if is_frontend:
        exclusions = [
            # Build and cache directories
            "node_modules",
            "node_modules/*",
            ".next",
            ".next/*",
            "out",
            "build",
            "dist",
            ".cache",
            # Generated files
            "package-lock.json",
            "yarn.lock",
            ".tsbuildinfo",
            "*.tsbuildinfo",
            # Test and coverage
            "coverage",
            "__tests__/coverage",
            ".nyc_output",
            # Static assets
            "public/images",
            "public/fonts",
            "public/*.ico",
            "public/*.png",
            "public/*.svg",
            # IDE and system files
            ".vscode",
            ".idea",
            ".DS_Store",
            # Storybook
            "storybook-static",
            ".storybook-build",
            # Environment files
            ".env",
            ".env.*",
            # Temporary files
            "*.log",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
        ]
    else:
        # Default exclusions for repo root or backend (keep digest manageable)
        exclusions = [
            # Exclude entire frontend for backend-only digest
            "frontend",
            "frontend/*",
            "frontend/**",
            # Python
            "__pycache__",
            "__pycache__/*",
            "*/__pycache__",
            "**/__pycache__/**",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
            ".pytest_cache",
            "venv",
            "venv/*",
            ".venv",
            "env",
            ".env",
            ".env.*",
            # Backend build/dist
            "build",
            "dist",
            "*.egg",
            # Alembic (optional: remove to include migrations in digest)
            "backend/alembic/versions",
            "backend/alembic/versions/*",
            "backend/alembic.ini",
            # Node/frontend at root
            "node_modules",
            "node_modules/*",
            "**/node_modules/**",
            "frontend/node_modules",
            "frontend/.next",
            "frontend/.next/*",
            "frontend/.next/**",
            "frontend/package-lock.json",
            "frontend/yarn.lock",
            "package-lock.json",
            "yarn.lock",
            ".next",
            ".next/*",
            "out",
            "build",
            "dist",
            ".cache",
            ".tsbuildinfo",
            "*.tsbuildinfo",
            # Version control and IDE
            ".git",
            ".gitignore",
            ".vscode",
            ".idea",
            ".DS_Store",
            "Thumbs.db",
            # Logs and temp
            "*.log",
            "*.tmp",
            "*.temp",
            "logs",
            # Docs and media (optional)
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.gif",
            "*.svg",
            "*.ico",
            "*.pdf",
            # Infra at root (optional: include if you want Docker/Makefile in digest)
            "Dockerfile",
            "Makefile",
            "docker-compose*.yml",
            ".env.example",
        ]

    if exclude_exts:
        exclusions.extend(f"*{ext}" for ext in exclude_exts)

    if is_frontend:
        include_patterns = [
            "*.tsx",
            "*.ts",
            "*.jsx",
            "*.js",
            "*.css",
            "*.scss",
            "*.sass",
            "*.less",
            "*.module.css",
            "*.module.scss",
            "*.module.sass",
            "*.module.less",
            "*.json",
            "*.html",
        ]
        cmd += ["-i", ",".join(include_patterns)]

    if exclusions:
        patterns = ",".join(exclusions)
        cmd += ["-e", patterns]

    log.info(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        log.info(f"Digest written to {output_file}")
    except subprocess.CalledProcessError as e:
        log.error(f"Error during gitingest execution: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.error(
            "Usage: python make_ingest.py <path_or_url> [output_file] [--frontend] [excluded_exts...]"
        )
        sys.exit(1)

    source = sys.argv[1]
    output_file = "digest.txt"
    exclude_exts = []
    is_frontend = False

    args = sys.argv[2:]
    while args:
        arg = args.pop(0)
        if arg == "--frontend":
            is_frontend = True
        elif arg.startswith("."):
            exclude_exts.append(arg)
        else:
            output_file = arg

    if not is_frontend and (
        "frontend" in source.lower() or "front-end" in source.lower()
    ):
        is_frontend = True
        log.info("Detected frontend directory, using frontend-specific processing...")

    generate_digest_cli(source, output_file, exclude_exts, is_frontend)
