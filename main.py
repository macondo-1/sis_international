from modules.project_class.main import Project
from modules.csv_tools.main import get_project_info_from_filename, fix_columns_to_match_db, read_file_pandas, fix_data_before_insert_to_db
from modules.utilities.main import get_information_from_blast_master_excel
from modules.million_verifier_api.million_verifier_api import verify_email
from modules.database.database import connect_to_db, insert_new_recruits, get_all_emails_to_dedupe, insert_update_recruits, insert_new_csv_to_db
import pprint
from pathlib import Path

if __name__ == '__main__':
    # CHECK: THIS NEEDS TO BE A DATABASE METHOD
    file_path = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/to_process/alberto/1198501_cafamerica_apollo_bison.csv')

    insert_new_csv_to_db(file_path)