import modules.constants.main as const
import datetime
import pandas as pd
import re
import json

today = datetime.datetime.today()


def get_information_from_blast_master_excel(it_project_number:str) -> dict:
    """
    Retrieves the information from the blast master excel as a dictionary
    it uses the it project number
    """
    df = pd.read_excel(const.blast_master_excel_path)
    df.dropna(subset='Unnamed: 1', inplace=True)
    df['Unnamed: 0'] = df['Unnamed: 0'].astype(int)
    df['Unnamed: 1'] = df['Unnamed: 1'].astype(int)
    df['Unnamed: 0'] = df['Unnamed: 0'].astype(str)
    df['Unnamed: 1'] = df['Unnamed: 1'].astype(str)
    df.rename(columns={
        'Unnamed: 0':'project_number',
        'Unnamed: 1':'it_project_number'
    }, inplace=True)
    df.set_index('it_project_number', inplace=True)

    inf_dict = df.loc[it_project_number,:].to_dict()

    return inf_dict

def fix_filename(filename:str) -> str:
    """
    Fixes the filename by:
    1. replaces white spaces for underscores
    2. removes all non-ascii characters
    3. replaces considered punctuation marks for underscores:
    3.1 .
    3.2 ,
    3.3 __
    3. adds date as suffix of the filename
    """

    global today
    today = today.strftime('%Y%m%d')
    filename = filename.replace(' ','_')
    filename = filename.replace('.','_')
    filename = filename.replace(',','_')
    filename = filename.replace('__','_')
    filename = filename.encode('ascii', errors='ignore').decode('ascii')
    filename = '{0}_{1}'.format(filename, today)
    return filename

# CHECK: include words boundaries to regex pattern
def find_matching_columns(keywords:list, current_column_names:list) -> list:
    """
    returns all column names that matches a keyword for the current column name
    """
    keywords = [x.lower() for x in keywords]
    pattern = '|'.join(keywords)
    pattern = re.compile(pattern)
    matching_columns = [x for x in current_column_names if re.search(pattern,x)]

    return matching_columns

def create_new_column_mapper(current_column_names:list) -> dict:
    """
    logic to input the key (current column name) and the value (new column name)
    returns the mapper as a dictionary
    """

    column_mapper = {}
    for current_column_name in current_column_names:
        print(current_column_name)

        # PENDING - prints suggested columns (regex pattern using each word as keyword)
        keywords = current_column_name.split(' ')
        matching_columns = find_matching_columns(keywords, const.DB_COLUMNS)
        print('suggested matching columns: {}'.format(matching_columns))
        print('all columns: {}'.format(const.DB_COLUMNS))

        new_column_name = input('new column name: ')
        column_mapper.update({current_column_name:new_column_name})
        print('')

    return column_mapper

def save_new_column_mapper(mapper_name: str, mapper_values:dict):
    """
    Opens the mapper
    Appends a new columns mapper
    Saves the mapper with the newly added dictionary
    """
    # open mapper
    file_path = const.DATABASE_MAPPERS_PATH
    with open(file_path, 'r') as file:
        mappers_dict = json.load(file)
        
    # append new values
    mappers = mappers_dict.get('mappers')
    new_entry = {
        'name': mapper_name,
        'map': mapper_values
    }
    mappers.append(new_entry)
    mappers_dict.update({'mappers':mappers})

    # save mapper
    with open(file_path, 'w') as file:
        json.dump(mappers_dict, file, indent=4)

if __name__ == '__main__':
    filename = fix_filename(filename ="My .name, is  Ståle")
    print(filename)