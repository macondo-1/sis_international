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