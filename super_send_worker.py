import modules.database.database as db
import modules.constants.main as const
from modules.super_send.super_send import SuperSend
from modules.million_verifier_api.million_verifier_api import MillionVerifier
import os
import sys
import csv
import logging

logging.basicConfig(filename=const.SS_LOG_FILE, encoding='utf-8', level=logging.DEBUG, format='%(levelname)s: %(asctime)s - %(message)s')


def acquire_lock():
    if os.path.exists(const.SS_LOCK_FILE_PATH):
        logging.info('Lock file. Exiting program.')
        sys.exit()
    open(const.SS_LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(const.SS_LOCK_FILE_PATH):
        os.remove(const.SS_LOCK_FILE_PATH)

def prepare_fetched_data_to_supersend(data: list[tuple]) -> list[dict]:
    ss_data = []

    for x in data:
        recruit_dict = {}
        recruit_dict['first_name'] = x[1]
        recruit_dict['email'] = x[2]
        ss_data.append(recruit_dict)

    return ss_data

def main():
    logging.info('STARTING LOOP')
    logging.info('Getting blasts quota...')
    data = db.get_today_blast_quota()
    logging.info('DONE!')

    if not data:
        logging.warning('No projects to work on!')


    for project in data:
        project_id = project[1]
        data = db.get_project_limit(project_id)
        limit = int(data[0][0])
        if limit < 0:
            limit = 0
        try:
            project_name = db.get_project_name_with_project_number(project_id)[0]
        except Exception as e:
            print('error: {}'.format(e))
            continue
        logging.info('Processing project {0} - {1}...'.format(project_id, project_name))
        logging.info('Getting records for SuperSend...')
        data = db.get_ss_ready_records(project_id, limit)
        recruits_ids = [x[0] for x in data]
        len_records = len(recruits_ids)
        logging.info('Got {} records!'.format(len_records))

        data = prepare_fetched_data_to_supersend(data)

        contacts = data
        campaign_id = db.get_ss_campaign_id(project_id)
        if len_records >= 1:
            logging.info('Uploading records to SuperSend...')
            super_send = SuperSend()
            data = super_send.bulk_create_contacts(contacts=contacts, campaign_id=campaign_id)
            if data != None:
                logging.info('SS Upload successful!')
                db.update_project_recruits_last_sent(project_id, recruits_ids)
            else:
                logging.warning('Error uploading records to SuperSend')



    data_mm = db.get_today_mm_quota()
    for project in data_mm:
        project_id = project[1]
        try:
            project_name = db.get_project_name_with_project_number(project_id)[0]
        except Exception as e:
            print('error: {}'.format(e))
            continue
        logging.info('Processing project {0} - {1}...'.format(project_id, project_name))
        logging.info("Checking if there's active jobs in MillionVerifier...")
        jobs = db.get_active_validation_jobs_for_project(project_id)
        len_jobs = jobs[0]
        if len_jobs != 0:
            logging.info('Got {} active jobs, skipping for now!'.format(len_jobs))
        else:
            logging.info('No active jobs. Getting records for MillionVerifier...')
            data = db.get_project_limit_mm(project_id)
            try:
                limit = int(data[0][0])
            except:
                limit = 0
            data = db.get_mv_ready_records(project_id, limit)
            recruits_ids = [x[0] for x in data]
            len_mv_records = len(recruits_ids)
            lines = [list(x) for x in data]
            lines = [x[1:] for x in data]

            if len_mv_records < 1:
                logging.info('Got {} records for MillionVerifier, skipping for now!'.format(len_mv_records))
            else:
                logging.info('Uploading {} to MillionVerifier...'.format(len_mv_records))
                to_validate_file_name = '/Users/albertoruizcajiga/python/sis_international/modules/million_verifier_api/temp/to_validate_{}.csv'.format(project_id)

                with open(to_validate_file_name, 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(['first_name', 'email'])
                    writer.writerows(lines)

                million_verifier = MillionVerifier()

                mv_upload_data = million_verifier.file_upload(to_validate_file_name, str(project_id))
                db.add_new_million_verifier_job(mv_upload_data, project_id)
                logging.info('Upload successful!')

    logging.info('FINISHED LOOP\n')


if __name__ == '__main__':
    acquire_lock()
    try:
        main()
    finally:
        release_lock()
