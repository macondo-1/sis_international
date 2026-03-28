from modules.project_class.main import Project
import pandas as pd
import datetime
import modules.constants.main as const
from modules.utilities.main import create_new_column_mapper, save_new_column_mapper
import json
import traceback
import numpy as np
import time
import logging
import sys
import shutil

readers = {
    '.csv' : pd.read_csv,
    '.xlsx': pd.read_csv,
    '.xls': pd.read_csv
}

today_date_ = datetime.datetime.now()
today_date_database = today_date_.strftime('%Y-%m-%d')
today_date = today_date_.strftime('%Y%m%d')

def get_project_info_from_filename() -> dict:
    """
    Loads project information from file name.
    Expected file name patterns:
    1. ItProjectNumber_ListName
    returns 
    """

    try:
        filename = '1_test'
        project_number, file_name = filename.split('_',1)
        project = Project(project_number=project_number, )
        project_dict = project.load_project()

        return project_dict
    
    except Exception as e:
        print('Failed getting project dict from file name', '\nerror message: ', e)

def read_file_pandas(file_path):
    """
    Reads a file using pandas
    """
    global readers
    file_extension = file_path.suffix
    reader = readers.get(file_extension)
    if reader is None:
        raise ValueError('No reader found for file extension: {0}'.format(file_extension))
    
    df = reader(file_path, on_bad_lines='skip', low_memory=False)

    return df

def clean_list_manually(df):
    print('Available columns: \n\n{0}\n'.format(df.columns.to_list()))
    first_name_col = str(input('first name column: '))
    email_col = input('email column: ')
    additional_columns = input('select additional columns (separated by commas):')

# CHECK: very long function, re factor it
def fix_columns_to_match_db(df, file_path, source='', status='', project_id = ''):
    """
    Fixes the csv file to match database columns using pandas
    """
    global today_date    

    try:
        columns = pd.Series(df.columns)

        # open mapper
        mapper_file_path = const.DATABASE_MAPPERS_PATH
        with open(mapper_file_path, 'r') as file:
            mappers_dict = json.load(file)

        list_mapper_name = None
        for x in mappers_dict['mappers']:
            mapper_keys = pd.Series(x['map'].keys())

            # if columns.isin(mapper_keys).all():
            if set(columns) == set(mapper_keys):
                list_mapper_name = x['name']
                break
        
        if not list_mapper_name:
            logging.info('No mapper saved, need to process manually!')
            print('No column mapper found, please create a new one!')
            # shutil.move(file_path, const.MANUAL_CLEANING_DIR / file_path.name)
            # sys.exit()
            # return

            try:
                mapper_values = create_new_column_mapper(columns)
                mapper_name = input('New column mapper name: ')
                mapper_name = '{}_{}'.format(mapper_name,today_date)
                save_new_column_mapper(mapper_name, mapper_values)

                # CHECK: This section is repeating the code from above, find a better way
                with open(mapper_file_path, 'r') as file:
                    mappers_dict = json.load(file)
                list_mapper_name = None
                for x in mappers_dict['mappers']:
                    mapper_keys = pd.Series(x['map'].keys())

                    if columns.isin(mapper_keys).all():
                        list_mapper_name = x['name']
                        break
            except Exception as e:
                print('failed creating new column mapper')
                print('error message: ', e)


        # CHECK: the list comprehensions seems weird, maybe i can avoid the past for loop if I include everything in the
        # list comprehension?
        time.sleep(.3)
        list_mapper = [x for x in mappers_dict['mappers'] if x['name'] == list_mapper_name][0]
        df = df.rename(columns = list_mapper['map'])
        df = df[list_mapper['map'].values()]

        # filling metadata
        file_name = file_path.stem
        available_sources = mappers_dict['sources']

        # if not source:
        #     source = input('Please provide the source of the list\n{0}\nSource: '.format(str(available_sources)))
        # available_statuses = mappers_dict['statuses']
        # if not status:
        #     status = input('Please provide the status of the records\n{0}\nStatus: '.format(str(available_statuses)))
        
        file_names = []
        file_names.append(file_name)
        df['file_name'] = str(file_names)
        sources = []
        sources.append(source)
        df['source'] = str(sources)
        df['creation_date'] = today_date_database
        df['last_update'] = today_date_database
        df['status'] = status
        if source == 'survey_monkey':
            df['opt-in'] = 1
        
        # CHECK: the following if should deprecate this one
        # # is it wise to have these two conditionals here?
        # if not project_id and not 'projects_ids' in df.columns:
        #     project_id = input('Please provide the internal project ID: ')
        # projects_ids = []
        # projects_ids.append(project_id)
        # df['projects_ids'] = str(projects_ids)

        if not 'projects_ids' in df.columns:
            # if not project_id:
            #     project_id = input('Please provide the internal project ID\n(click enter if not for a project): ')
            projects_ids = []
            projects_ids.append(project_id)
            df['projects_ids'] = str(projects_ids)

        # deleting all non-database columns
        db_columns = [x for x in const.DB_COLUMNS if x in df.columns]
        df = df[db_columns]
        for column in db_columns:
            df[column] = df[column].apply(lambda x: str(x) if x is not np.nan else None)

    except Exception as e:
        print('failed fixing columns to match database')
        print('error message: ', e)
        traceback.print_exc()
        exit

    return df


def fix_columns_to_match_db_manual(df, file_path, source='', status='', project_id = ''):
    """
    Fixes the csv file to match database columns using pandas
    """
    global today_date    

    try:
        columns = pd.Series(df.columns)

        # open mapper
        mapper_file_path = const.DATABASE_MAPPERS_PATH
        with open(mapper_file_path, 'r') as file:
            mappers_dict = json.load(file)

        list_mapper_name = None
        for x in mappers_dict['mappers']:
            mapper_keys = pd.Series(x['map'].keys())

            # if columns.isin(mapper_keys).all():
            if set(columns) == set(mapper_keys):
                list_mapper_name = x['name']
                break
        
        if not list_mapper_name:
            logging.info('No mapper saved, need to process manually!')
            print('No column mapper found, please create a new one!')
            # shutil.move(file_path, const.MANUAL_CLEANING_DIR / file_path.name)
            # # sys.exit()
            # return

            try:
                mapper_values = create_new_column_mapper(columns)
                mapper_name = input('New column mapper name: ')
                mapper_name = '{}_{}'.format(mapper_name,today_date)
                save_new_column_mapper(mapper_name, mapper_values)

                # CHECK: This section is repeating the code from above, find a better way
                with open(mapper_file_path, 'r') as file:
                    mappers_dict = json.load(file)
                list_mapper_name = None
                for x in mappers_dict['mappers']:
                    mapper_keys = pd.Series(x['map'].keys())

                    if columns.isin(mapper_keys).all():
                        list_mapper_name = x['name']
                        break
            except Exception as e:
                print('failed creating new column mapper')
                print('error message: ', e)


        # CHECK: the list comprehensions seems weird, maybe i can avoid the past for loop if I include everything in the
        # list comprehension?
        time.sleep(.3)
        list_mapper = [x for x in mappers_dict['mappers'] if x['name'] == list_mapper_name][0]
        df = df.rename(columns = list_mapper['map'])
        df = df[list_mapper['map'].values()]

        # filling metadata
        file_name = file_path.stem
        available_sources = mappers_dict['sources']

        # if not source:
        #     source = input('Please provide the source of the list\n{0}\nSource: '.format(str(available_sources)))
        # available_statuses = mappers_dict['statuses']
        # if not status:
        #     status = input('Please provide the status of the records\n{0}\nStatus: '.format(str(available_statuses)))
        
        file_names = []
        file_names.append(file_name)
        df['file_name'] = str(file_names)
        sources = []
        sources.append(source)
        df['source'] = str(sources)
        df['creation_date'] = today_date_database
        df['last_update'] = today_date_database
        df['status'] = status
        
        # CHECK: the following if should deprecate this one
        # # is it wise to have these two conditionals here?
        # if not project_id and not 'projects_ids' in df.columns:
        #     project_id = input('Please provide the internal project ID: ')
        # projects_ids = []
        # projects_ids.append(project_id)
        # df['projects_ids'] = str(projects_ids)

        if not 'projects_ids' in df.columns:
            # if not project_id:
            #     project_id = input('Please provide the internal project ID\n(click enter if not for a project): ')
            projects_ids = []
            projects_ids.append(project_id)
            df['projects_ids'] = str(projects_ids)

        # deleting all non-database columns
        db_columns = [x for x in const.DB_COLUMNS if x in df.columns]
        df = df[db_columns]
        for column in db_columns:
            df[column] = df[column].apply(lambda x: str(x) if x is not np.nan else None)

    except Exception as e:
        print('failed fixing columns to match database')
        print('error message: ', e)
        traceback.print_exc()
        exit

    return df


def fix_data_before_insert_to_db(df:pd.DataFrame) -> pd.DataFrame:
    """
    Matches columns datatypes to those expected by the database
    """
    lower_columns = ['first_name', 'last_name', 'email']
    lower_columns = [x for x in lower_columns if x in df.columns]

    for column in lower_columns:
        df[column] = df[column].apply(lambda x: str(x).lower().strip() if x is not None else None)
        # df[column] = df[column].str.lower().str.strip()

    return df

def get_project_info(project_id, df_blastmaster):

    try:
        df_blastmaster1 = df_blastmaster.astype({'Unnamed: 1': 'str'})
        df_blastmaster1['Unnamed: 1'] = df_blastmaster1['Unnamed: 1'].apply(lambda x: x.split('.')[0])
        df_blastmaster1 = df_blastmaster1.set_index('Unnamed: 1')
        project_info = df_blastmaster1.loc[str(project_id)]

        return project_info
    except:
        print('Error getting project information for {0}'.format(project_id))

    

def add_message_to_mm_list(mm_list_total_length):
    """
    Reads from all files in directory
    creates a file combining all files
    only saves a certain amount per project total_q/q_of_projects
    saves the rest of the records per project in a pending directory
    """
    try:
        FROM_NAME = 'Ruth Stanat'

        #reading file names
        all_filenames = [i for i in const.MAILING_PATH.glob('*.csv')]
        records_per_project = int(mm_list_total_length/len(all_filenames))

        df_blast_master = pd.read_excel(const.BLAST_MASTER_PATH)
        #df_blast_master = df_blast_master.set_index('Unnamed: 1')

        # Iterating over each csv and creating mail message per record and
        # creating project number column (look up where is this needed?)
        for file_name in all_filenames:
            p_number = file_name.name.split('_')[0]
            project_info1 = list_.get_project_info(file_name.name, df_blast_master)
            MESSAGE = project_info1['Blast Message']

            df = pd.read_csv(file_name)
            df = df.rename(columns={'first_name':'First_name',
                                    'email':'Email',
                                    })
            df = df.replace({'First_name':'None'},'Colleague')
            df = df.replace({'First_name':np.nan},'Colleague')
            df['message'] = df.apply(lambda row: MESSAGE.format(First_name=row['First_name'], FROM_NAME=FROM_NAME), axis=1)
            df['project_number'] = p_number

            # CHECK: this 0 value is hardcoded, should exist a better way
            if mm_list_total_length == 0:
                df.to_csv(file_name, index = False)
            else:
                # Saving csv files
                df[:records_per_project].to_csv(file_name, index = False)

                # CHECK: inspect the df, if empty, do not save it
                # check if the destination dir has a file with the same name, if so merge them
                # if file_name in iterdir():
                #   concat df with saved file
                #   save concatenated file
                df[records_per_project:].to_csv(const.PENDING_MAILING_PATH.joinpath(file_name.name), index = False)
            
        
        concatenated_df = pd.concat([pd.read_csv(f,low_memory=False) for f in all_filenames])
        concatenated_df = concatenated_df.sort_values(by='Email', ascending=True)
        concatenated_df = concatenated_df[['Email','First_name','message','project_number']]
        
        filename_out = const.MAILING_PATH.joinpath('mm_list.csv')
        concatenated_df.to_csv(filename_out, index = False)

        mm_list_len = len(concatenated_df)
        print("\nnew mm list length: {mm_list_len}\n".format(mm_list_len=mm_list_len))

        for file_name in all_filenames:
            os.remove(file_name)

    except Exception as e:
        print('failed creating the MM list, check all file names {0}'.format(file_name))
        print(e)
        print(traceback.format_exc())