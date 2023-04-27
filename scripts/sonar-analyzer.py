import os
import csv
from github import Github
import git


JAVA_PROJECTS_LIST_FILE = 'inputs/projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = 'inputs/projects-python-test.txt'
CSHARP_PROJECTS_LIST_FILE = 'inputs/projects-csharp-test.txt'

PROJECTS_DIR = "/u/23/chrens1/unix/Sonar/ESEM/projects"
JAVA_BUILD_TYPES_FILE = 'inputs/projects-java-build.txt'
JAVA_BUILD_TYPE_DICT = {}

SONAR_PLUGIN = 'id "org.sonarqube" version "3.5.0.2730"'
SONAR_TOKEN = 'squ_2b538bab99a18a124554d34ccc4a97702ffe9ca2'
SONAR_URL = 'http://localhost:9000'

GRADLE_COMMAND = f'./gradlew sonar \
  -Dsonar.projectKey=csharp-test \
  -Dsonar.host.url={SONAR_URL} \
  -Dsonar.login={SONAR_TOKEN}'

github = Github()


def check_gradle_path(project_dir):
    if not os.path.exists(f'{project_dir}/build.gradle'):
        print(f"build.gradle does not exist in {project_dir}.")
        return False
    return True

def add_sonar_plugin_to_gradle(project_dir):
    if not check_gradle_path():
        return None

    with open(f'{project_dir}/build.gradle', 'r') as build_file:
        file_contents = build_file.read()

        if "plugins {" in file_contents:

            start_plugin_pos = file_contents.index("plugins {")
            end_plugin_pos = file_contents.index("}", start_plugin_pos) + 1

            plugins_section = file_contents[start_plugin_pos:end_plugin_pos]

            if SONAR_PLUGIN in plugins_section:
                print(f"The plugin entry {SONAR_PLUGIN} already exists in the plugins section.")
                return None

            updated_plugins_section = plugins_section.replace("}", f"\n\t{SONAR_PLUGIN}\n}}")

            updated_file_contents = file_contents.replace(plugins_section, updated_plugins_section)
        else:
            updated_file_contents = file_contents.replace("dependencies {", f"plugins {{\n\t{SONAR_PLUGIN}\n}}\n\ndependencies {{")

    with open(f'{project_dir}/build.gradle', 'w') as build_file:
        build_file.write(updated_file_contents)

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
    if lang == 'csharp':
        repo_names = parse_repo_names(CSHARP_PROJECTS_LIST_FILE)
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
    os.system(f'cd {project_dir}')
    os.system(command)


def get_language_command(project_name, project_dir, project_release, lang):
    command =''
    if lang == 'java':
        command = get_java_command(project_name,project_dir,project_release)
    if lang == 'python':
        command = get_python_command(project_name,project_dir,project_release)
    if lang == 'csharp':
        command = get_csharp_command(project_name, project_dir, project_release)

    return command

def get_java_command(project_name, project_dir, project_release):
    build_type = JAVA_BUILD_TYPE_DICT[project_name]

    if build_type == 'maven':
        command = f'mvn clean verify sonar:sonar \
                    -Dsonar.projectKey={project_name}-{project_release} \
                    -Dsonar.projectBaseDir={project_dir} \
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


def get_csharp_command(project_name, project_dir, project_release):
    command = ''


if __name__ == '__main__':
    JAVA_BUILD_TYPE_DICT = parse_java_build_config_to_dict(JAVA_BUILD_TYPES_FILE)

    analyze_projects('python')

 ##
    # analyze_projects('java')

    # analyze_projects('csharp')


