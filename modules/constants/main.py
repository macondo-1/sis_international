# All path and secret variables are sourced from environment variables via
# config.py. This file re-exports them under their original names so that
# existing callers (workers, modules) require no import changes.

from config import (
    # secrets
    SS_API_KEY,
    MV_API_KEY,
    APOLLO_API_KEY,
    GODADDY_PASSWORD,
    BCC_PASSWORD,
    SHUBHA_BCC_PASSWORD,
    INCENTIVES_BCC_PASSWORD,
    # database
    SQLITE_DB_PATH as database_path,
    # base / campaign paths
    BASE_PATH,
    BLAST_MASTER_PATH,
    MM_READY_CSV,
    MAILING_PATH,
    LOG_PATH,
    GODADDY_EMAILS_PATH,
    BCC_FOOTER_PATH,
    # local working directories
    TEMP_DIR,
    TEMP_DB_DIR,
    MV_TEMP_DIR,
    DATABASE_INPUT_DIR,
    FAILED_DATABASE_INPUT_DIR,
    MANUAL_CLEANING_DIR,
    # local file paths
    DATABASE_MAPPERS_PATH,
    FOOTER_PATH,
    # lock files
    DB_LOCK_FILE_PATH,
    SS_LOCK_FILE_PATH,
    MV_LOCK_FILE_PATH,
    SMTP_LOCK_FILE_PATH,
    BCC_LOCK_FILE_PATH,
    # log files
    SS_LOG_FILE,
    MV_LOG_FILE,
    DB_LOG_FILE,
    SMTP_LOG_FILE,
    BCC_LOG_FILE,
)

# Paths derived from BASE_PATH — kept as computed values rather than separate
# env variables to avoid redundancy. If BASE_PATH changes, these follow.
projects_base_path = BASE_PATH / 'sis_international_files' / 'projects'
db_file_path = BASE_PATH / 'sis_international_files' / 'database' / 'sis_database.db'

# Legacy alias used by modules/utilities
blast_master_excel_path = BLAST_MASTER_PATH

# ---------------------------------------------------------------------------
# Static constants — not environment-dependent
# ---------------------------------------------------------------------------

DB_COLUMNS = [
    'first_name', 'last_name', 'age', 'date_of_birth', 'gender',
    'ethnicity', 'nationality', 'education', 'email', 'other_emails',
    'phone_number', 'linkedin', 'facebook', 'twitter', 'other_links',
    'country', 'state', 'city', 'zip_code', 'job_title', 'industry',
    'company_name', 'job_keywords', 'file_name', 'source', 'creation_date',
    'last_update', 'projects_ids', 'status', 'email_validation', 'is_active',
]

SOURCES = ['apollo', 'qualtrics']

SMTP_HOST = 'smtp.office365.com'
SMTP_PORT = 587

GODADDY_EMAILS = """
Available emails:


ruthstanat@sisinternationalresearch.net
ruthstanat@sisresearch.org

Select email: """
