import modules.database.database as db
import modules.constants.main as const
from modules.million_verifier_api.million_verifier_api import MillionVerifier
import os
import sys
import logging
import traceback

logging.basicConfig(filename=const.MV_LOG_FILE, encoding='utf-8', level=logging.DEBUG, format='%(levelname)s: %(asctime)s - %(message)s')


def acquire_lock():
    if os.path.exists(const.MV_LOCK_FILE_PATH):
        logging.info('Lock!')
        sys.exit()
    open(const.MV_LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(const.MV_LOCK_FILE_PATH):
        os.remove(const.MV_LOCK_FILE_PATH)

def download_and_process_all_available_lists_on_mv():
    logging.info('STARTING LOOP')
    jobs = db.get_processing_jobs()
    if not jobs:
        logging.info('Nothing to download from MillionVerifier!')
        logging.info('FINISHED LOOP\n')
        return

    for (job_id,) in jobs:
        try:
            mv_handler = MillionVerifier()
            file_info_dict = mv_handler.file_info(job_id)
            status = file_info_dict['status']
            project_id = file_info_dict['file_name']

            if status == 'finished':
                project_name = db.get_project_name_with_project_number(project_id)[0]
                logging.info('Downloading {0} - {1}...'.format(project_id, project_name))
                mv_report = mv_handler.download_report(job_id)
                validated_file_name = const.MV_TEMP_DIR / 'validated_{}.csv'.format(job_id)
                mv_handler.save_csv_file(mv_report, validated_file_name)
                logging.info('Updating validation status... ')
                db.update_validation_status(validated_file_name)
                os.remove(validated_file_name)
                db.update_mv_job_status(job_id, 'completed')
                logging.info('DONE!')

        except Exception as e:
            logging.warning(f"Error processing MillionVerifier job {job_id}: {e}")
            print('traceback:')
            traceback.print_exc()

    logging.info('FINISHED LOOP\n')

if __name__ == '__main__':
    acquire_lock()
    try:
        download_and_process_all_available_lists_on_mv()
    finally:
        release_lock()
