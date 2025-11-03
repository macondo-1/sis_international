from modules.project_class.main import Project

if __name__ == '__main__':
    handler = Project()
    project_dict = handler.load_project()
    print(project_dict)