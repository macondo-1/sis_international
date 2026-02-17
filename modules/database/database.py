# CHECK: do i need a connect to db func? or should i connect per func?

import sqlite3
from pathlib import Path
import csv
import modules.constants.main as const
from modules.csv_tools.main import read_file_pandas, fix_columns_to_match_db, fix_data_before_insert_to_db
import os
import pandas as pd
import ast
import json
from datetime import datetime

# CHECK: other_emails should be added as a list

def connect_to_db(): # CHECK why this fails? -> tuple(sqlite3.Connection, sqlite3.Cursor):
    """
    Connects to the database and returns a cursor
    """
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    
    return conn, cursor

# CHECK:  instead of insert or ignore, I need to retrieve all emails first so I can update them instead of inserting them
# CHECK: insert_new_recruits and insert_update_recruits should be just one function
# CHECK: insert_into_table might just be the one function
def insert_new_recruits(file_path) -> None:
    """
    Inserts all records found in a csv file into the recruits database
    """
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        headers_str = ', '.join(headers)
        placeholders = ', '.join(['?'] * len(headers))
        query = 'INSERT OR IGNORE INTO recruits ({0}) VALUES ({1})'.format(headers_str, placeholders)
        rows_to_insert = []
        for row in reader:
            row = [None if value == "" else value for value in row]
            rows_to_insert.append(row)

    cursor.executemany(query, rows_to_insert)
    conn.commit()
    conn.close()

def insert_update_recruits(file_path) -> None:
    """
    Inserts all records found in a csv file into the pending_update table database
    """
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        headers_str = ', '.join(headers)
        placeholders = ', '.join(['?'] * len(headers))
        query = 'INSERT OR IGNORE INTO pending_update ({0}) VALUES ({1})'.format(headers_str, placeholders)
        
        rows_to_insert = []
        for row in reader:
            row = [None if value == "" else value for value in row]
            rows_to_insert.append(row)

    cursor.executemany(query, rows_to_insert)
    conn.commit()
    conn.close()

def insert_into_table(file_path, table_name) -> None:
    """
    Inserts all records found in a csv file into a table in the database
    """
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        headers_str = ', '.join(headers)
        placeholders = ', '.join(['?'] * len(headers))
        query = 'INSERT OR IGNORE INTO {0} ({1}) VALUES ({2})'.format(table_name, headers_str, placeholders)
        
        rows_to_insert = []
        for row in reader:
            row = [None if value == "" else value for value in row]
            rows_to_insert.append(row)

    cursor.executemany(query, rows_to_insert)
    conn.commit()
    conn.close()

def add_new_column_to_db():
    pass

def execute_query():
    pass

def create_table_for_unassigned_columns():
    """
    in case there are columns that do not match the db schema
    i can store these columns in a table referencing (ids) to the main database.
    later i can go back to this tables to assign to existing columns or new ones
    """
    pass

def get_all_unassigned_columns_tables():
    """
    gets table names so i can work on them
    """
    pass

def update_records_with_unassigned_columns():
    """
    once the columns are mapped (either to an exisiting column or by creating a new one)
    update the records in the main table with the now assigned columns
    """
    pass

# CHECK: might be good to rename to something else than dedupe since its going to be used to determine records to update too (maybe instead)
def get_update_records(list_of_emails:list) -> pd.DataFrame:
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    batch = []
    all_emails = []
    df = pd.DataFrame(columns=['ID', 'email', 'other_emails', 'other_links', 'file_name', 'source', 'projects_ids'])
    while list_of_emails:
        batch = list_of_emails[:1000]
        list_of_emails = list_of_emails[1000:]

        placeholders = ', '.join(['?'] * len(batch))

        query = """SELECT ID, email, other_emails, other_links, file_name, source, projects_ids
        FROM recruits
        WHERE email IN ({0})""".format(placeholders)

        cursor.execute(query, batch)
        emails = cursor.fetchall()
        for x in emails:
            try:
                df.loc[len(df)] = x
            except:
                print(x)  
        # df.set_index('ID', inplace=True)

    conn.close()

    return df

# DEPRECATED
# def insert_new_csv_to_db(file_path, source, status, project_id):
#     """
#     Processes files into the database
#     it loads new recruits into recruits table and
#     loads repeated recruits into pending_update table
#     """
#     df = read_file_pandas(file_path)
#     df = fix_columns_to_match_db(df, file_path, source, status, project_id)
#     df = fix_data_before_insert_to_db(df)

#     # Getting duplicate emails
#     list_of_emails = list(df.email)
#     update_records = get_update_records(list_of_emails)
#     emails = list(update_records.email)

#     # Saving duplicate emails
#     df_duplicate_recruits = df[df['email'].isin(emails)]
#     duplicate_emails_path = '{0}_duplicates.csv'.format(file_path.stem)
#     duplicate_emails_path = const.TEMP_DB_DIR.joinpath(duplicate_emails_path)
#     df_duplicate_recruits.to_csv(duplicate_emails_path, index=False)
#     insert_update_recruits(duplicate_emails_path)
#     os.remove(duplicate_emails_path)

#     # Saving new emails
#     df_new_recruits = df[~df['email'].isin(emails)]
#     new_emails_path = const.TEMP_DB_DIR.joinpath(file_path.name)
#     df_new_recruits.to_csv(new_emails_path, index=False)
#     insert_new_recruits(new_emails_path)
#     os.remove(new_emails_path)

def insert_new_csv_to_db(file_path, source, status, project_id):
    """
    Processes files into the database
    it saves new recruits and updates recruits
    """
    df = read_file_pandas(file_path)
    df = fix_columns_to_match_db(df, file_path, source, status, project_id)
    df = fix_data_before_insert_to_db(df)

    # Getting duplicate emails
    list_of_emails = list(df.email)
    update_records = get_update_records(list_of_emails)
    emails = list(update_records.email)

    ########################
    # Saving new emails
    df_new_recruits = df[~df['email'].isin(emails)]
    new_emails_path = const.TEMP_DB_DIR.joinpath(file_path.name)
    df_new_recruits.to_csv(new_emails_path, index=False)
    print('saving new records...')
    insert_new_recruits(new_emails_path)
    q_new_recruits = len(df_new_recruits)
    print('inserted {0} new records'.format(q_new_recruits))
    os.remove(new_emails_path)

    ########################
    # Saving update emails
    new_data = df[df['email'].isin(emails)]
    prepared_new_data = prepare_update_records(update_records, new_data)
    update_emails_path = '{0}_updates.csv'.format(file_path.stem)
    update_emails_path = const.TEMP_DB_DIR.joinpath(update_emails_path)
    prepared_new_data.to_csv(update_emails_path, index=False)
    q_update_recruits = len(prepared_new_data)
    print('updating {0} records'.format(q_update_recruits))
    bulk_update_records(update_emails_path)
    os.remove(update_emails_path)

# CHECK: seems like the following two are the same?
def bulk_update_records(table_name:str):
    """
    
    """

    conn, cursor = connect_to_db()

    data_to_update = [('sandra', 'paschall', 1)] # (new_value, id)

    cursor.execute("BEGIN TRANSACTION;")
    for new_value_1, new_value_2, row_id in data_to_update:
        cursor.execute("UPDATE recruits SET first_name = ?, last_name = ? WHERE id = ?", (new_value_1,new_value_2, row_id))
    conn.commit()
    conn.close()
    
def bulk_update_records(file_path:Path, table_name:str = 'recruits') -> None:
    """
    Inserts all records found in a csv file into a table in the database
    """
    conn, cursor = connect_to_db()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        headers = [x for x in headers if x != 'ID']
        set_clause = ", ".join([f"{header} = ?" for header in headers])
        query = 'UPDATE {0} SET {1} WHERE ID = ?'.format(table_name, set_clause)
        
        rows_to_insert = []
        for row in reader:
            row = [None if value == "" else value for value in row]
            rows_to_insert.append(row)

    cursor.executemany(query, rows_to_insert)

    # try:
    #     cursor.executemany(query, rows_to_insert)
    # except Exception as e:
    #     print('error: ', e)
    #     # df = pd.DataFrame(rows_to_insert,columns=headers)
    #     print(query)
    #     print(rows_to_insert[0])

    conn.commit()
    conn.close()

base_queries = {
    'select' : 'SELECT {0} FROM {1}',
    'update' : 'UPDATE {0} SET',
    'insert' : "INSERT OR IGNORE INTO {0}"
}

def build_select_query(table_name:str, columns_str:str):
    """
    main table
    1. insert new values
    1. extract for project
    2. update with mail status (sends, failed, etc)
    3. update unassigned columns records

    mail events table
    1. read "in-queue" records
    2. update with mail status (sends, failed, etc)
    3. 
    """

    query = 'SELECT {columns} FROM {table_name}'.format(table_name=table_name, columns_str=columns_str)

    pass

def to_list(x):
    if isinstance(x, list):
        return x
    if pd.isna(x):   # handles None/NaN
        return []
    return [x]       # convert scalar to list

# CHECK: this function should not be in the database module
def prepare_update_records(update_records:pd.DataFrame, new_data) -> pd.DataFrame:
    """
    Handles the combination of data from the database and new csv before update in database
    it combines it extending the current list with the new value

    List columns:
    - other emails (this might be best if I save other emails as new records and link to the main record somehow)
    - other links
    - file name
    - source
    - projects_ids    
    """

    list_type_columns = ['other_emails', 'other_links', 'file_name', 'source', 'projects_ids']
    for x in list_type_columns:
        try:
            update_records[x] = update_records[x].apply(lambda x: ast.literal_eval(x) if x is not None else None)
        except:
            print('failed converting to list in the column: ')
            print(x)

    merged_df = update_records.merge(new_data,on='email',how='outer')

    for x in list_type_columns:
        x_str = x + '_x'
        y_str = x + '_y'
        if x_str in merged_df.columns:
            merged_df[x] = merged_df.apply(
                lambda row: to_list(row[x_str]) + to_list(row[y_str]),
                axis=1
            )

            merged_df = merged_df.drop(y_str, axis=1)
            merged_df = merged_df.drop(x_str, axis=1)

    columns = merged_df.columns
    columns_new = list(columns[1:])
    columns_new.append(columns[0])
    merged_df = merged_df[columns_new]

    merged_df = merged_df.drop(columns=['creation_date'], errors='ignore')

    return merged_df

def update_validation_status(file_path: Path):

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        email_position = headers.index('email')
        validation_position = headers.index('result')
        to_db = []

        for x in reader:
            value = (x[validation_position], x[email_position])
            to_db.append(value)

    query = """UPDATE recruits SET email_validation = ? WHERE email = ?"""
    conn, cursor = connect_to_db()
    cursor.executemany(query, to_db)
    conn.commit()
    conn.close()
    print('success!')

def query_complement_for_million_verifier():

    mv_query = "WHERE email_validation NOT IN (ok, invalid, catch_all)"

    ss_query = "WHERE email_validation = ok OR " \
    ""

def add_new_million_verifier_job(data:json, project_id:str) -> None:
    """
    example json imput:
    {'file_id': '30258177',
    'file_name': 'test',
    'status': 'unknown',
    'unique_emails': 0,
    'updated_at': '2026-02-17 05:38:51',
    'createdate': '2026-02-17 05:38:51',
    'percent': 0,
    'total_rows': 0,
    'verified': 0,
    'unverified': 0,
    'ok': 0,
    'catch_all': 0,
    'disposable': 0,
    'invalid': 0,
    'unknown': 0,
    'reverify': 0,
    'credit': 0,
    'estimated_time_sec': 0,
    'error': ''}
    """
    conn, cursor = connect_to_db()
    headers = ['job_id', 'status', 'project_id']
    headers_str = ','.join(headers)
    placeholders = ', '.join(['?'] * len(headers))
    query = 'INSERT OR IGNORE INTO million_verifier_jobs ({0}) VALUES ({1})'.format(headers_str, 
                                                                                    placeholders)
    values = (data['file_id'], data['status'], project_id)
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def get_processing_jobs():
    conn, cursor = connect_to_db()
    cursor.execute("SELECT job_id FROM million_verifier_jobs WHERE status='processing'")
    return cursor.fetchall()

def update_mv_job_status(job_id, status, output_path=None):
    conn, cursor = connect_to_db()
    cursor.execute("""
        UPDATE million_verifier_jobs 
        SET status=?, updated_at=?, output_path=? 
        WHERE job_id=?
    """, (status, datetime.utcnow(), output_path, job_id))
    conn.commit()
    

# query to select all matches
# create table projects_recipients
# query to save matches to projects_recipients
# query to extract N elements from recruits considering projects_recipients
# query to save extractions into mail_events
