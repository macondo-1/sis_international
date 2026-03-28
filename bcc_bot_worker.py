from modules.bcc_bot.main import send_emails_selenium_concurrency
from modules.database.database import choose_bcc_account, get_project_limit_mm, get_project_name_with_project_number, get_today_mm_quota, get_mailmerge_ready_records
from modules.csv_tools.main import get_project_info
import modules.constants.main as const

import logging
import os
import pandas as pd
import csv
import sys

logging.basicConfig(filename=const.BCC_LOG_FILE, encoding='utf-8', level=logging.INFO, format='%(levelname)s: %(asctime)s - %(message)s')


def acquire_lock():
    if os.path.exists(const.SMTP_LOCK_FILE_PATH):
        sys.exit()
    open(const.SMTP_LOCK_FILE_PATH, "w").close()

def release_lock():
    if os.path.exists(const.SMTP_LOCK_FILE_PATH):
        os.remove(const.SMTP_LOCK_FILE_PATH)

def create_mm_list():
    logging.info('STARTING LOOP') 
    logging.info('Getting blasts quota...') 
    data = get_today_mm_quota()
    logging.info('DONE!') 
    
    if not data:
        logging.warning('No projects to work on!') 
        logging.info('FINISHED LOOP\n')
        return 

    df_blast_master = pd.read_excel(const.BLAST_MASTER_PATH)
    mm_list = []
    for project in data:
        project_id = project[1]

        project_info = get_project_info(project_id, df_blast_master)
        message = project_info['Blast Message']
        
        data = get_project_limit_mm(project_id)
        limit = int(data[0][0])
        if limit < 0:
            limit = 0
        try:
            project_name = get_project_name_with_project_number(project_id)[0]
        except Exception as e:
            print('error: {}'.format(e))
            continue
        logging.info('Processing project {0} - {1}...'.format(project_id, project_name)) 
        logging.info('Getting records for Mailmerge...')

        data = get_mailmerge_ready_records(project_id, limit)
        recruits_ids = [x[0] for x in data]
        len_records = len(recruits_ids)
        mm_list_ = [(project_id, x) for x in recruits_ids]

        mm_list_ = [(x[0], x[1], x[2], message.format(First_name=str(x[1]).split(' ')[0].capitalize(), FROM_NAME='Ruth Stanat'), project_id) for x in data]

        logging.info('Got {} records!'.format(len_records)) 
        mm_list.extend(mm_list_)
    

    logging.info('FINISHED LOOP\n') 
    if mm_list:
        with open(const.MM_READY_CSV, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['id','First_name','Email','message', 'project_id'])
            writer.writerows(mm_list)


def send_out_mm_list():
    logging.info('STARTING LOOP') 
    if not const.MM_READY_CSV.exists():
        logging.info("there's no mailmerge list. Skipping for now...")
        logging.info('FINISHED LOOP\n')
        sys.exit()

    logging.info('Sending out mailerge list...')
    # CHECK: Need to log the email sending as it happens
    data = choose_bcc_account()
    if not data:
        logging.info('No available accounts!') 
        logging.info('FINISHED LOOP\n')
        exit()
    hourly_remaining = data[4] - data[6]
    daily_remaining = data[3] - data[5]
    remaining = min(hourly_remaining, daily_remaining)
    if remaining < 0:
        remaining = 0
    email_account = data[1]
    email_id = data[0]

    cc = None
    FROM_EMAIL = email_account
    slice_size = 100
    send_emails_selenium_concurrency(cc, FROM_EMAIL, slice_size, email_id, remaining)

    logging.info('DONE!') 
    logging.info('FINISHED LOOP\n')



if __name__ == '__main__':
    acquire_lock()
    try:
        create_mm_list()
        send_out_mm_list()
    finally:
        release_lock()
