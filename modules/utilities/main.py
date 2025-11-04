import modules.constants.main as const
import datetime
import pandas as pd

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

if __name__ == '__main__':
    filename = fix_filename(filename ="My .name, is  Ståle")
    print(filename)