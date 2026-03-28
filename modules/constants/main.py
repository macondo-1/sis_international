# PATHS
from pathlib import Path

BASE_PATH = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities')
projects_base_path = BASE_PATH.joinpath('sis_international_files', 'projects')
db_file_path = BASE_PATH.joinpath('sis_international_files','database','sis_database.db')

blast_master_excel_path = BASE_PATH.joinpath('blast_master_good_final.xlsx')

# CHECK: change this path once the final location is defined
database_path = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/sis_international.db')

# VALUES (?)

DB_COLUMNS = ['first_name', 'last_name', 'age', 'date_of_birth', 'gender',
       'ethnicity', 'nationality', 'education', 'email', 'other_emails',
       'phone_number', 'linkedin', 'facebook', 'twitter', 'other_links',
       'country', 'state', 'city', 'zip_code', 'job_title', 'industry',
       'company_name', 'job_keywords', 'file_name', 'source', 'creation_date',
       'last_update', 'projects_ids', 'status', 'email_validation',
       'is_active']

DATABASE_MAPPERS_PATH = Path('/Users/albertoruizcajiga/python/sis_international/files/utilities/database_mappers.json')

SOURCES = ['apollo','qualtrics']

TEMP_DB_DIR = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp')

TEMP_DIR = Path('/Users/albertoruizcajiga/python/sis_international/files/temp')

MV_TEMP_DIR = Path('/Users/albertoruizcajiga/python/sis_international/modules/million_verifier_api/temp')

MV_LOCK_FILE_PATH = Path('/Users/albertoruizcajiga/python/sis_international/modules/million_verifier_api/temp/mv_lock_file.lock')

SS_LOCK_FILE_PATH = Path('/Users/albertoruizcajiga/python/sis_international/modules/super_send/temp/ss_lock_file.lock')

DATABASE_INPUT_DIR = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/pending_database_input')

DB_LOCK_FILE_PATH  = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/db_lock_file.lock')

FAILED_DATABASE_INPUT_DIR = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/pending_database_input/failed_files')

SS_LOG_FILE = Path('/Users/albertoruizcajiga/python/sis_international/files/logs/ss_cron.log')

MV_LOG_FILE = Path('/Users/albertoruizcajiga/python/sis_international/files/logs/mv_cron.log')

DB_LOG_FILE = Path('/Users/albertoruizcajiga/python/sis_international/files/logs/db_cron.log')

MANUAL_CLEANING_DIR = Path('/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/pending_database_input/manual_cleaning_needed')


MM_READY_CSV = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/mailing_bot/alberto/mm_list.csv')
FOOTER_PATH = Path('/Users/albertoruizcajiga/python/sis_international/modules/smtp_bot/files/footer.txt')
SMTP_HOST = 'smtp.office365.com'
SMTP_PORT = 587
GODADDY_PASSWORD = '***REMOVED***'
GODADDY_EMAILS = """
Available emails:

ruthstanat@sisinternationalresearch.net
ruthstanat@sisresearch.org

Select email: """

LOG_PATH = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/log/log.csv')

GODADDY_EMAILS_PATH = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/godaddy_emails.csv')

SMTP_LOG_FILE = Path('/Users/albertoruizcajiga/python/sis_international/files/logs/smtp_cron.log')

SMTP_LOCK_FILE_PATH = Path('/Users/albertoruizcajiga/python/sis_international/modules/super_send/temp/smtp_lock_file.lock')

BLAST_MASTER_PATH = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/blast_master_good_final.xlsx')