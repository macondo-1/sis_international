# CHECK: do i need a connect to db func? or should i connect per func?

import sqlite3
from pathlib import Path
import csv
import modules.constants.main as const
from modules.csv_tools.main import read_file_pandas, fix_columns_to_match_db, fix_data_before_insert_to_db
import os

def connect_to_db():
    """
    Connects to the database and returns a cursor
    """
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    
    return conn, cursor

# CHECK:  instead of insert or ignore, I need to retrieve all emails first so I can update them instead of inserting them
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
        print(query)
        cursor.executemany(query, reader)
    conn.commit()
    conn.close()

def insert_update_recruits(file_path) -> None:
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
        query = 'INSERT OR IGNORE INTO pending_update ({0}) VALUES ({1})'.format(headers_str, placeholders)
        print(query)
        cursor.executemany(query, reader)
    conn.commit()
    conn.close()

def add_new_column_to_db():
    pass

def build_query():
    """
    main table
    1. insert new values
    1. extract for project
    2. update with mail status (sends, failed, etc)
    3. update unassigned columns records
    4. update mail verification

    mail events table
    1. read "in-queue" records
    2. update with mail status (sends, failed, etc)
    3. 
    """
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

def get_all_emails_to_dedupe(list_of_emails:list) -> list:
    conn = sqlite3.connect(const.database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    placeholders = ', '.join(['?'] * len(list_of_emails))

    query = """SELECT email
    FROM recruits
    WHERE email IN ({0})""".format(placeholders)

    cursor.execute(query, list_of_emails)
    emails = cursor.fetchall()
    emails = [x[0] for x in emails]

    return emails

def insert_new_csv_to_db(file_path):
    """
    Processes files into the database
    it loads new recruits into recruits table and
    loads repeated recruits into pending_update table
    """
    df = read_file_pandas(file_path)
    df = fix_columns_to_match_db(df, file_path)
    df = fix_data_before_insert_to_db(df)

    # Getting duplicate emails
    list_of_emails = list(df.email)
    emails = get_all_emails_to_dedupe(list_of_emails)

    # Saving duplicate emails
    df_duplicate_recruits = df[df['email'].isin(emails)]
    duplicate_emails_path = '{0}_duplicates.csv'.format(file_path.stem)
    duplicate_emails_path = const.TEMP_DB_DIR.joinpath(duplicate_emails_path)
    df_duplicate_recruits.to_csv(duplicate_emails_path, index=False)
    insert_update_recruits(duplicate_emails_path)
    os.remove(duplicate_emails_path)

    # Saving new emails
    df_new_recruits = df[~df['email'].isin(emails)]
    new_emails_path = const.TEMP_DB_DIR.joinpath(file_path.name)
    df_new_recruits.to_csv(new_emails_path, index=False)
    insert_new_recruits(new_emails_path)
    os.remove(new_emails_path)
