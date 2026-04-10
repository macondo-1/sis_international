import modules.database.database as db
import modules.constants.main as const
import os
import shutil
from pathlib import Path
import sys
import time
import logging

logging.basicConfig(filename=const.DB_LOG_FILE, encoding='utf-8', level=logging.DEBUG, format='%(levelname)s: %(asctime)s - %(message)s')

def acquire_lock():
    if os.path.exists(const.DB_LOCK_FILE_PATH):
        sys.exit()
    open(const.DB_LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(const.DB_LOCK_FILE_PATH):
        os.remove(const.DB_LOCK_FILE_PATH)

def main():
    logging.info('STARTING LOOP')
    file_names = list(const.DATABASE_INPUT_DIR.glob('*.csv'))
    if not file_names:
        logging.info('Nothing to insert into the database!')
        logging.info('FINISHED LOOP\n')
        return

    for file_path in const.DATABASE_INPUT_DIR.glob('*.csv'):
        new_file_name = file_path.name
        source = ''
        project_id = ''
        if '--' in new_file_name:
            source = new_file_name.split('--')[0]
            new_file_name = new_file_name.split('--')[1]
        if '__' in new_file_name:
            project_id = new_file_name.split('__')[0]
            new_file_name = new_file_name.split('__')[1]

        try:
            # logging.info('Preparing csv for database input...')
            # prepare_csv_for_database_input(file_path, source=source, project_id=project_id, status='cold')
            # logging.info('DONE!')

            logging.info('Inserting file %s...', Path(file_path).name)
            data = db.insert_new_csv_to_db(file_path)
            ids = data[0]
            logging.info('DONE!')
            if project_id:
                # check: uncaught error if project name cannot be obtained
                # check: doesnt work if project is not in project table before
                project_name = db.get_project_name_with_project_number(project_id)[0]
                logging.info('Saving for project {0} - {1}'.format(project_id, project_name))
                db.save_newly_added_records_to_project(project_id, ids)
                logging.info('DONE!')
            time.sleep(1)
        except Exception as e:
            logging.warning('Failed inserting new csv to database and assigning it to a project blast./nError: {}'.format(e))
            new_path = const.FAILED_DATABASE_INPUT_DIR / Path(file_path).name
            shutil.move(file_path, new_path)
            logging.info('Moved to failed files directory...')
    logging.info('FINISHED LOOP\n')

if __name__ == '__main__':
    acquire_lock()
    try:
        main()
    finally:
        release_lock()
