import modules.constants.main as const
import pandas as pd

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



