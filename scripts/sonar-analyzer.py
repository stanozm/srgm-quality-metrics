import os
import csv
from github import Github
import git


JAVA_PROJECTS_LIST_FILE = 'inputs/projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = 'inputs/projects-python-test.txt'


PROJECTS_DIR = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/Sonarqube"
JAVA_BUILD_TYPES_FILE = 'inputs/projects-java-build.txt'
JAVA_BUILD_TYPE_DICT = {}

SONAR_PLUGIN = 'id "org.sonarqube" version "3.5.0.2730"'
SONAR_TOKEN = 'sqa_fd21d6bd9bf0f60af5e343e06ce59467c4b2f90b'
SONAR_URL = 'http://localhost:9000'



github = Github()




def parse_java_build_config_to_dict(filename):
    dict = {}
    with open(filename, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            dict[row[0]] = row[1]
    return dict



def get_repo_releases(github_repo):
    releases = github_repo.get_releases()
    return releases



def analyze_projects(lang):
    repo_names = parse_repo_names_lang(lang)

    for repo_name in repo_names:
        print('Processing repo: ' + repo_name)
        repo = get_repo(repo_name)
        cloned_repo = clone_repo(repo)
        releases = get_repo_releases(repo)

        for rel in releases:
            print(f"Processing Release: {rel.tag_name}")
            cloned_repo_tag_ref = cloned_repo.tags[rel.tag_name].commit
            cloned_repo.git.checkout(cloned_repo_tag_ref, force=True)
            repo_dir = cloned_repo.working_dir
            execute_sonar(repo_name.split("/")[1],repo_dir,rel.tag_name, lang)
            print('-' * 20)


def parse_repo_names_lang(lang):
    if lang == 'java':
        repo_names = parse_repo_names(JAVA_PROJECTS_LIST_FILE)
    if lang == 'python':
        repo_names = parse_repo_names(PYTHON_PROJECTS_LIST_FILE)
    return repo_names

def parse_repo_names(path_to_repos_file):
    with open(path_to_repos_file) as inputFile:
        repos_list = inputFile.read().splitlines()
    return repos_list

def get_repo(repo_name):
    repo = github.get_repo(repo_name)
    return repo

def clone_repo(github_repo):
    repo_dir = f'{PROJECTS_DIR}/{github_repo.name}'
    cloned_repo = git.Repo.clone_from(github_repo.git_url.replace("git://", "https://"), repo_dir)
    return cloned_repo

def execute_sonar(project_name, project_dir, project_release,lang):
    command = get_language_command(project_name, project_dir, project_release, lang)
    print('Executing command: ' + command)
    #os.system(f'cd {project_dir}')
    change_folder = f'cd {project_dir} && '
    os.system(change_folder + command)


def get_language_command(project_name, project_dir, project_release, lang):
    command =''
    if lang == 'java':
        command = get_java_command(project_name,project_dir,project_release)
    if lang == 'python':
        command = get_python_command(project_name,project_dir,project_release)

    return command

def get_java_command(project_name, project_dir, project_release):


    command = f'mvn clean verify sonar:sonar \
                    -Dsonar.projectKey={project_name}-{project_release} \
                    -Dsonar.projectBaseDir={project_dir} \
                    -Dsonar.projectName={project_name}-{project_release} \
                    -Dsonar.host.url={SONAR_URL} \
                    -Dsonar.login={SONAR_TOKEN}'

    return command


def get_python_command(project_name, project_dir, project_release):
    command = f'sonar-scanner \
  -Dsonar.projectKey={project_name}-{project_release} \
  -Dsonar.projectBaseDir={project_dir} \
  -Dsonar.sources=. \
  -Dsonar.host.url={SONAR_URL} \
  -Dsonar.login={SONAR_TOKEN}'
    return command






if __name__ == '__main__':
    #JAVA_BUILD_TYPE_DICT = parse_java_build_config_to_dict(JAVA_BUILD_TYPES_FILE)

    analyze_projects('python')


    #analyze_projects('java')

    # analyze_projects('csharp')


