from modules.project_class.main import Project
from modules.csv_tools.main import get_project_info_from_filename
from modules.utilities.main import get_information_from_blast_master_excel
import pprint

if __name__ == '__main__':
    it_project_number = '1545031'
    # project_name = 'uw_qual_usa'
    # # project = Project(project_number=project_number, project_name=project_name)
    # project = Project()
    # print(project.number)

    inf_dict = get_information_from_blast_master_excel(it_project_number=it_project_number)
    project_number = inf_dict['project_number']
    project_name = inf_dict['project_name']
    project = Project(project_number=project_number, project_name=project_name)
    project_dict = project.load_project()

    pprint.pprint(project_dict)