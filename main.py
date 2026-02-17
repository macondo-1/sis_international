from modules.project_class.main import Project
from modules.csv_tools.main import get_project_info_from_filename, fix_columns_to_match_db, read_file_pandas, fix_data_before_insert_to_db
from modules.utilities.main import get_information_from_blast_master_excel
from modules.database.database import connect_to_db, insert_new_recruits, get_update_records, insert_update_recruits, insert_new_csv_to_db, bulk_update_records, prepare_update_records, update_validation_status, add_new_million_verifier_job, get_processing_jobs, update_mv_job_status
from modules.super_send.super_send import SuperSend
from modules.million_verifier_api.million_verifier_api import MillionVerifier
import pprint
from pathlib import Path
import os
import pandas as pd
import modules.constants.main as const
import csv
import json
import sys
from datetime import datetime

temp_dir = Path("files/temp")
mv_temp_dir = Path("modules/million_verifier_api/temp")

LOCK_FILE_PATH = temp_dir / 'check_jobs.lock'

def save_new_ru_files_to_db():
    path_ = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/ramped_up_database')
    paths = path_.glob('*.csv')
    processed_files_path = const.TEMP_DB_DIR.joinpath('processed_files.txt')
    failed_files_path = const.TEMP_DB_DIR.joinpath('failed_files.txt')

    with open(processed_files_path, 'r') as file:
        lines = file.readlines()
    lines = [x.strip() for x in lines]

    with open(failed_files_path, 'r') as file:
        bad_lines = file.readlines()
    bad_lines = [x.strip() for x in bad_lines]

    lines.extend(bad_lines)
    to_process_paths = [str(x) for x in paths if str(x) not in lines]

    for file_path in to_process_paths:

        try:

            with open(processed_files_path, 'r') as file:
                lines = file.readlines()
            lines = [x.strip() for x in lines]

            file_path = Path(file_path)
            source, status, project_id = 'ramped_up','cold',' '
            insert_new_csv_to_db(file_path, source, status, project_id)

            lines.append(str(file_path))

            with open(processed_files_path, 'w') as file:
                content = '\n'.join(lines)
                file.write(content)

        except Exception as e:
            print('error:', e)
            print('saving file name to failed files text file...')
            with open(failed_files_path, 'r') as file:
                bad_lines = file.readlines()
            bad_lines = [x.strip() for x in bad_lines]
            bad_lines.append(str(file_path))
            with open(failed_files_path, 'w') as file:
                content = '\n'.join(bad_lines)
                file.write(content)
            print('saved succesfully!')

def query_to_csv(query_str: str, out_path: str):
    conn, cursor = connect_to_db()
    print('connected succesfully')
    cursor.execute(query_str)
    print('query executed succesfully')
    with open(out_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(d[0] for d in cursor.description)
        writer.writerows(cursor.fetchall())
    conn.close()

def query_project_needs(sql_file_path: str, limit: int):
    with open(sql_file_path, 'r') as file:
        query = file.read()
    query = query.format(limit=limit)
    conn, cursor = connect_to_db()
    print('connected succesfully')
    cursor.execute(query)
    print('query executed succesfully')

    data = cursor.fetchall()
    conn.close()
    return data

def prepare_fetched_data_to_supersend(data: list[tuple]) -> list[dict]:
    ss_data = []

    for x in data:
        recruit_dict = {}
        recruit_dict['first_name'] = x[0]
        recruit_dict['email'] = x[1]
        ss_data.append(recruit_dict)
    
    return ss_data

def acquire_lock():
    if os.path.exists(LOCK_FILE_PATH):
        sys.exit()
    open(LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(LOCK_FILE_PATH):
        os.remove(LOCK_FILE_PATH)

def download_and_process_all_available_lists_on_mv():
    jobs = get_processing_jobs()
    if not jobs:
        print('nothing to process')
        return

    for (job_id,) in jobs:
        try:
            mv_handler = MillionVerifier()
            file_info_dict = mv_handler.file_info(job_id)
            status = file_info_dict['status']

            if status == 'finished':
                mv_report = mv_handler.download_report(job_id)
                validated_file_name = mv_temp_dir / 'validated_{}.csv'.format(job_id)
                mv_handler.save_csv_file(mv_report, validated_file_name)
                print('updating validation status... ', job_id)
                update_validation_status(validated_file_name)
                print('update done')
                os.remove(validated_file_name)
                update_mv_job_status(job_id, 'completed')

        except Exception as e:
            print(f"Error processing MillionVerifier job {job_id}: {e}")
    

if __name__ == '__main__':
    acquire_lock()
    try:
        download_and_process_all_available_lists_on_mv()
    finally:
        release_lock()
    
    # # CONTINUE THIS
    # blast_needs_file_path = '/Users/albertoruizcajiga/Downloads/blast.csv'
    # sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/base_query.sql'

    # # Gets and fixes blast needs
    # # CHECK: need to save campaign_id to json
    # with open(blast_needs_file_path, 'r') as file:
    #     reader = csv.DictReader(file)
    #     blast_needs = {'blast_needs' : []}
    #     for x in reader:
    #         if x['\ufeffproject_id']:
    #             cleaned_str = x[' q '].strip().replace(',','')
    #             project_needs = {'project_id': x['\ufeffproject_id'],
    #                              'total_records': int(float(cleaned_str)),
    #                              'remaining_records': int(float(cleaned_str))}
    #             blast_needs['blast_needs'].append(project_needs)

    # blast_needs_path = temp_dir / 'blast_needs.json'
    # with open(blast_needs_path, 'w') as file:
    #     json.dump(blast_needs, file)

    # # print(blast_needs)

    
    # for x in blast_needs['blast_needs']:
    #     try:
    #         # Gets records and fixes them for supersend
    #         limit = int(x['remaining_records'])
    #         data = query_project_needs(sql_file_path, limit)
    #         # CHECK: if len(data) <= 0 break the loop for this project
    #         data = prepare_fetched_data_to_supersend(data)

    #         # Uploads contacts to a supersend campaign
    #         contacts = data
    #         campaign_id = '21df4491-7929-43b8-a2eb-e6483f6248c0'
    #         super_send = SuperSend()
    #         data = super_send.bulk_create_contacts(contacts=contacts, campaign_id=campaign_id)
    #         print(data)

    #         if data['success']:
    #             x['remaining_records'] = x['remaining_records'] - len(contacts)
    #             with open(blast_needs_path, 'w') as file:
    #                 json.dump(blast_needs, file)

        # HERE
        # try:
        #     # DELETE
        #     blast_needs_path = temp_dir / 'blast_needs.json'
        #     sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/base_query.sql'
            
        #     with open(blast_needs_path, 'r') as file:
        #         blast_needs = json.load(file)

        #     for x in blast_needs['blast_needs']:
        #         # Gets remaining records for email validation
        #         limit = int(x['remaining_records'])
        #         data = query_project_needs(sql_file_path, limit)
                
        #         to_validate_file_name = mv_temp_dir / 'validating_{}.csv'.format(x['project_id'])
        #         with open(to_validate_file_name, 'w') as file:
        #             writer = csv.writer(file)
        #             writer.writerow(['first_name', 'email'])
        #             writer.writerows(data)

        #     # MV upload
        #         million_verifier = MillionVerifier()
        #         # mv_upload_data = million_verifier.file_upload(to_validate_file_name, x['project_id'])
        #         # mv_file_id = mv_upload_data['file_id']

        #         mv_file_id = '30257592' # DELETE
        #         file_status = million_verifier.file_info(mv_file_id)
        #         if file_status['status'] == 'finished':
        #             mv_report = million_verifier.download_report(mv_file_id)
        #             validated_file_name = mv_temp_dir / 'validated_{}.csv'.format(x['project_id'])
        #             print(validated_file_name)
        #             million_verifier.save_csv_file(mv_report, validated_file_name)
        #             print('updating... ', x['project_id'])
        #             update_validation_status(Path(validated_file_name))
        #             print('update done')

        #         break


        #     # REPEAT # Gets records and fixes them for supersend

        #     # REPEAT # Uploads contacts to a supersend campaign

        #     # REPEAT # Gets remaining records for email validation (while loop until remaining records are zero)

        
        # except Exception as e:
        #     print('SuperSend part error: ', e)




    # # MAKE THIS A DATABASE MODULE
    # sql_file_path = '/Users/albertoruizcajiga/python/sis_international/modules/database/files/temp/test_sql.sql'
    # with open(sql_file_path, 'r') as file:
    #     query = file.read()

    # out_path = '/Users/albertoruizcajiga/Downloads/valid_tucson_usa_to_validate_internal_db.csv'
    # query_to_csv(query, out_path)

    # MAKE THIS A DATABASE MODULE
    # dir_path = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/to_process/alberto')
    # for x in dir_path.glob('*.csv'):
    #     print('updating... ', x.name)
    #     update_validation_status(x)
    #     print('update done')

    # path = '/Users/albertoruizcajiga/Downloads/nyc_snov_FULL_REPORT_MILLIONVERIFIER.COM.csv'
    # update_validation_status(path)

    # MAKE THIS A DATABASE MODULE
    # dir_path = Path('/Users/albertoruizcajiga/Library/CloudStorage/GoogleDrive-beautifulday874@gmail.com/My Drive/Information_Technology/alberto/utilities/to_process/alberto')
    # for x in dir_path.glob('*.csv'):
    #     print('inserting... ', x.name)
    #     insert_new_csv_to_db(x, source="", status='cold', project_id="")
    #     print('insertion done')