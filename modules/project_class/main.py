import json
from pathlib import Path
import sqlite3
import csv
from collections import defaultdict
import modules.constants.main as const

class Project:
    projects_base_path = const.projects_base_path
    db_file_path = const.db_file_path

    base_filter_dict = {
        'country':[None],
        'state':[None],
        'city':[None],
        'gender':[None],
        'age':[None],
        'ethnicity':[None],
        'nationality':[None],
        'zip_code':[None],
        'job_title':[None],
        'education':[None],
        'company_name':[None],
        'projects_id':[None],
        'file_name':[None],
        'last_contact_date':[None],
    }

    def __init__(self, project_number:str = None, project_name:str = None):
        if (not project_number and not project_name):
            self.name = input('Project name: ')
            self.number = input('Project number: ')
            self.project_manager = input("Project manager's name: ")
            self.greenarrow_server = input("Green Arrow server: ")
            self.greenarrow_template_name = '{0}_{1}'.format(self.number[:-1], self.name) # modify: this might not be necessary if it can be built out of the attributes
        else:
            self.name = project_name
            self.number = project_number       

    def save_project(self):
        """
        Saves the project attributes into a json
        """
        directory_name = '{0}_{1}'.format(self.number, self.name)
        project_path = self.projects_base_path.joinpath(directory_name)
        if not project_path.is_dir():
            project_path.mkdir()

        file_name = '{}.json'.format(directory_name)
        json_path = project_path.joinpath(file_name)
        # modify: create this dict out of iterating over the attributes
        data = {
            'name':self.name,
            'number':self.number,
            'project_manager':self.project_manager,
            'greenarrow_server':self.greenarrow_server,
            'greenarrow_template_name':self.greenarrow_template_name
        }
        with open(json_path, 'w') as file:
            json.dump(data, file, indent=4)

        print('file saved to {}'.format(json_path))

    def load_project(self):
        """
        Reads a json with the project attributes
        returns the data as a dictionary
        """
        directory_name = '{0}_{1}'.format(self.number, self.name)
        project_path = self.projects_base_path.joinpath(directory_name)
        file_name = '{}.json'.format(directory_name)
        json_path = project_path.joinpath(file_name)
        if json_path.exists():
            with open(json_path, 'r') as file:
                project_dict = json.load(file)
        else:
            print('project file does not exists, try creating it.')
            project_dict = None

        self.project_dict = project_dict

        return project_dict

    def load_project_filter(self):
        """
        Reads a csv file with the project filters
        returns it as a dictionary with column names as keys and a list of keywords as value
        """
        directory_name = '{0}_{1}'.format(self.number, self.name)
        project_path = self.projects_base_path.joinpath(directory_name)
        file_name = '{}_filter.csv'.format(directory_name)
        csv_path = project_path.joinpath(file_name)
        print(csv_path)
        column_dict = defaultdict(set)  # Use set for deduplication

        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for key, value in row.items():
                    if value:  # Skip empty/null
                        cleaned_value = value.strip().lower()
                        if cleaned_value:
                            column_dict[key].add(cleaned_value)

        # Convert sets back to lists
        return {key: list(values) for key, values in column_dict.items()}

    def retrieve_records_from_db(self,full_query):
        """
        Reads the filters for the project
        parses the database
        saves matching records as a csv in project's folder
        returns the matching records
        """
        conn = sqlite3.connect(self.db_file_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(full_query)
        results = cursor.fetchall()
        conn.close()

        # Convert each row to a dictionary
        results = [dict(row) for row in results]

        # for row in results:
        #     print(row)

        return results

    def build_sqlite_query(self, filter_dict, table_name='survey_monkey'):
        base_query = "SELECT * FROM {}".format(table_name)
        conditions = []

        for field, values in filter_dict.items():
            
            if values == [None]:
                continue

            field_conditions = []
            for value in values:
                value = value.strip().lower()
                field_conditions.append(f"LOWER({field}) LIKE '%{value}%'")
            if field_conditions:
                conditions.append(f"({' OR '.join(field_conditions)})")

        if conditions:
            full_query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            full_query = base_query

        return full_query

    def save_sql_results_to_csv(self, results):
        """
        receives the results from the sql query
        saves it as csv
        """
        fieldnames = results[0].keys()
        file_name = self.cur_path.joinpath('test.csv') # modify: need to select the dir path and file name
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    def save_mail_message(self,mail_message):
        directory_name = '{0}_{1}'.format(self.number, self.name)
        project_path = self.projects_base_path.joinpath(directory_name)
        filename = project_path.joinpath('{}.txt'.format(directory_name))
        with open(filename,'w') as file:
            file.write(mail_message)
        

# if __name__ == '__main__':
#     handler = Project()
#     project_dict = handler.load_project()
#     print(project_dict)