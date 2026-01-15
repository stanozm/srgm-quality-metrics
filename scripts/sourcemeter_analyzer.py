import os
import sys
import subprocess as sp, shlex
from github import Github
import csv

import git

JAVA_PROJECTS_LIST_FILE = 'inputs/projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = 'inputs/projects-python-test.txt'

SOURCEMETER_PATH = "//u/23/chrens1/unix/utility/sourcemeter/SourceMeter-10.2.0-x64-Linux"
# PROJECTS_DIR =  "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/projects"
PROJECTS_DIR = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/Sourcemeter"

SOURCEMETER_JAVA_PARAMS = " -runFB=false" \
                     " -runAndroidHunter=false" \
                     " -runVulnerabilityHunter=false" \
                     " -runFaultHunter=false" \
                     " -runRTEHunter=false" \
                     " -runDCF=false" \
                     " -runMetricHunter=false" \
                     " -runMET=true" \
                     " -runPMD=false" \
                     " -runLIM2Patterns=false" \
                     " -runUDM=false"


# SOURCEMETER_PYTHON_PARAMS = " -runFaultHunter=false" \
#                      " -runDCF=false" \
#                      " -runMetricHunter=false" \
#                      " -runFaultHunter=false" \
#                      " -runMET=true" \
#                      " -runUDM=false" \
#                      " -pythonBinary=python3.7" \
#                      " -pythonVersion=3" \
#                      " -runPylint=false" \
#                      " -runLIM2Patterns=false" \
#                      " -runSQ=false"


SOURCEMETER_PYTHON_PARAMS = " -pythonBinary=python3.7" \
                     " -pythonVersion=3"


github = Github()




def parse_repo_names(path_to_repos_file):
    with open(path_to_repos_file) as inputFile:
        repos_list = inputFile.read().splitlines()
    return repos_list

def find_file_with_extension(folder_path, extension):
    relative_file_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(extension):
                relative_file_path = os.path.relpath(os.path.join(root, file), folder_path)
                relative_file_paths.append(relative_file_path)

    return relative_file_paths


def get_repo(repo_name):
    repo = github.get_repo(repo_name)
    return repo

def clone_repo(github_repo):
    repo_dir = f"{PROJECTS_DIR}/{github_repo.name}"

    if os.path.exists(repo_dir):
        return git.Repo(repo_dir)

    return git.Repo.clone_from(
        github_repo.git_url.replace("git://", "https://"),
        repo_dir
    )



def get_repo_releases(github_repo):
    releases = github_repo.get_releases()
    return releases



def execute_sourcemeter(project_name, project_dir, project_release,lang):
    command = get_language_command(project_name, project_dir, project_release, lang)
    print('Executing command: ' + command)
    os.system(command)


def get_language_command(project_name, project_dir, project_release, lang):
    command =''
    if lang == 'java':
        command = get_java_command(project_name,project_dir,project_release)
    if lang == 'python':
        command = get_python_command(project_name,project_dir,project_release)


    return command

def get_java_command(project_name, project_dir, project_release):
     command = f"{SOURCEMETER_PATH}/Java/AnalyzerJava " \
              + f"-resultsDir={PROJECTS_DIR}/../Results/Java " \
              + f"-projectName={project_name} " \
              + f"-currentDate={project_release} " \
              + f"-projectBaseDir={project_dir} " + SOURCEMETER_JAVA_PARAMS
     return command


def get_python_command(project_name, project_dir, project_release):
    command = f"{SOURCEMETER_PATH}/Python/AnalyzerPython " \
              + f"-resultsDir={PROJECTS_DIR}/../Results/Python " \
              + f"-projectName={project_name} " \
              + f"-currentDate={project_release} " \
              + f"-projectBaseDir={project_dir} " + SOURCEMETER_PYTHON_PARAMS
    return command


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

            add_init_files(repo_dir)

            try:
                execute_sourcemeter(repo_name.split("/")[1],repo_dir,rel.tag_name, lang)
            except Exception as e:
                print(e)
                continue
            print('-' * 20)


def parse_repo_names_lang(lang):
    if lang == 'java':
        repo_names = parse_repo_names(JAVA_PROJECTS_LIST_FILE)
    if lang == 'python':
        repo_names = parse_repo_names(PYTHON_PROJECTS_LIST_FILE)
    return repo_names


def add_init_files(root_path: str):
    for current_path, dirs, files in os.walk(root_path):

        has_py_files = any(
            f.endswith(".py") and f != "__init__.py"
            for f in files
        )

        if has_py_files:
            init_path = os.path.join(current_path, "__init__.py")

            if not os.path.exists(init_path):
                with open(init_path, "w", encoding="utf-8"):
                    pass
                print(f"Created: {init_path}")

def init(projects_dir_path):
    global PROJECTS_DIR
    PROJECTS_DIR = projects_dir_path



if __name__ == '__main__':
    analyze_projects('python')

 ##
    # analyze_projects('java')

    #analyze_projects('csharp')

