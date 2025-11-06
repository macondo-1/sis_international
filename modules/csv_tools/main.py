from modules.project_class.main import Project
import pandas as pd
import datetime
import modules.constants.main as const
from modules.utilities.main import create_new_column_mapper, save_new_column_mapper
import json
import traceback
import numpy as np

readers = {
    '.csv' : pd.read_csv,
    '.xlsx': pd.read_csv,
    '.xls': pd.read_csv
}

today_date_ = datetime.datetime.now()
today_date_database = today_date_.strftime('%Y-%m-%d')

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

def fix_columns_to_match_db(df, file_path):
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

            if columns.isin(mapper_keys).all():
                list_mapper_name = x['name']
                break
        
        if not list_mapper_name:
            print('No column mapper found, please create a new one!')
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
        list_mapper = [x for x in mappers_dict['mappers'] if x['name'] == list_mapper_name][0]
        df = df.rename(columns = list_mapper['map'])
        df = df[list_mapper['map'].values()]

        # filling metadata
        file_name = file_path.stem
        available_sources = mappers_dict['sources']
        source = input('Please provide the source of the list\n{0}\nSource: '.format(str(available_sources)))
        available_statuses = mappers_dict['statuses']
        status = input('Please provide the status of the records\n{0}\nStatus: '.format(str(available_statuses)))
        file_names = []
        file_names.append(file_name)
        df['file_name'] = str(file_names)
        sources = []
        sources.append(source)
        df['source'] = str(sources)
        df['creation_date'] = today_date_database
        df['last_update'] = today_date_database
        df['status'] = status
        project_id = input('Please provide the internal project ID: ')
        projects_ids = []
        projects_ids.append(project_id)
        df['projects_ids'] = str(projects_ids)
        df_str = df.astype(str)

    except Exception as e:
        print('failed fixing columns to match database')
        print('error message: ', e)
        traceback.print_exc()

    return df_str

def fix_data_before_insert_to_db(df:pd.DataFrame) -> pd.DataFrame:
    """
    Matches columns datatypes to those expected by the database
    """
    lower_columns = ['first_name', 'last_name', 'email']
    lower_columns = [x for x in lower_columns if x in df.columns]

    for column in lower_columns:
        df[column] = df[column].str.lower().str.strip()

    return df