from modules.project_class.main import Project

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