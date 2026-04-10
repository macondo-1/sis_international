"""
Central configuration module. Call load_dotenv() exactly once here.
All other modules should import from this file rather than calling
load_dotenv() or os.environ directly.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set.")
    return value


def _path(name: str) -> Path:
    return Path(_require(name))


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------

SS_API_KEY = _require("SS_API_KEY")
MV_API_KEY = _require("MV_API_KEY")
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY", "")  # optional — API not yet in use
GODADDY_PASSWORD = _require("GODADDY_PASSWORD")
BCC_PASSWORD = _require("BCC_PASSWORD")
SHUBHA_BCC_PASSWORD = _require("SHUBHA_BCC_PASSWORD")
INCENTIVES_BCC_PASSWORD = _require("INCENTIVES_BCC_PASSWORD")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

SQLITE_DB_PATH = _path("SQLITE_DB_PATH")

# ---------------------------------------------------------------------------
# Base / campaign paths (Google Drive or equivalent shared storage)
# ---------------------------------------------------------------------------

BASE_PATH = _path("BASE_PATH")
BLAST_MASTER_PATH = _path("BLAST_MASTER_PATH")
MM_READY_CSV = _path("MM_READY_CSV")
MAILING_PATH = _path("MAILING_PATH")
LOG_PATH = _path("LOG_PATH")
GODADDY_EMAILS_PATH = _path("GODADDY_EMAILS_PATH")
BCC_FOOTER_PATH = _path("BCC_FOOTER_PATH")

# ---------------------------------------------------------------------------
# Local working directories
# ---------------------------------------------------------------------------

TEMP_DIR = _path("TEMP_DIR")
TEMP_DB_DIR = _path("TEMP_DB_DIR")
MV_TEMP_DIR = _path("MV_TEMP_DIR")
DATABASE_INPUT_DIR = _path("DATABASE_INPUT_DIR")
FAILED_DATABASE_INPUT_DIR = _path("FAILED_DATABASE_INPUT_DIR")
MANUAL_CLEANING_DIR = _path("MANUAL_CLEANING_DIR")

# ---------------------------------------------------------------------------
# Local file paths
# ---------------------------------------------------------------------------

DATABASE_MAPPERS_PATH = _path("DATABASE_MAPPERS_PATH")
FOOTER_PATH = _path("FOOTER_PATH")

# ---------------------------------------------------------------------------
# Lock files — one per worker; never share a lock between workers
# ---------------------------------------------------------------------------

DB_LOCK_FILE_PATH = _path("DB_LOCK_FILE_PATH")
SS_LOCK_FILE_PATH = _path("SS_LOCK_FILE_PATH")
MV_LOCK_FILE_PATH = _path("MV_LOCK_FILE_PATH")
SMTP_LOCK_FILE_PATH = _path("SMTP_LOCK_FILE_PATH")
BCC_LOCK_FILE_PATH = _path("BCC_LOCK_FILE_PATH")  # previously shared with SMTP — now separate

# ---------------------------------------------------------------------------
# Log files
# ---------------------------------------------------------------------------

SS_LOG_FILE = _path("SS_LOG_FILE")
MV_LOG_FILE = _path("MV_LOG_FILE")
DB_LOG_FILE = _path("DB_LOG_FILE")
SMTP_LOG_FILE = _path("SMTP_LOG_FILE")
BCC_LOG_FILE = _path("BCC_LOG_FILE")
