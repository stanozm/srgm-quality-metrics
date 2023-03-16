import os
import sys
import subprocess as sp, shlex
from github import Github

import git

JAVA_PROJECTS_LIST_FILE = 'projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = ''
CSHARP_PROJECTS_LIST_FILE = ''


SOURCEMETER_PATH = "/u/23/chrens1/unix/SourceMeter"
SOURCEMETER_JAVA_PARAMS = " -runFB=false" \
                     " -runAndroidHunter=false" \
                     " -runVulnerabilityHunter=false" \
                     " -runFaultHunter=false" \
                     " -runRTEHunter=false" \
                     " -runDCF=false" \
                     " -runMetricHunter=false" \
                     " -runMET=false"

SOURCEMETER_PYTHON_PARAMS = ''

SOURCEMETER_CSHARP_PARAMS = ''


PROJECTS_DIR =  "/u/23/chrens1/unix/SourceMeter/ESEM/projects"



github = Github()


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



def get_repo_releases(github_repo):
    releases = github_repo.get_releases()
    return releases

def execute_sourcemeter(project_name, project_dir, project_release,lang):
    command = get_language_command(project_name, project_dir, project_release, lang)
    print('Executing command: ' + command)
    os.system(command)


def get_language_command(project_name, project_dir, project_release, lang):
    switch ={
        'java': get_java_command(project_name,project_dir,project_release),
        'python': get_python_command(project_name,project_dir,project_release),
        'csharp': get_csharp_command(project_name,project_dir,project_release)
    }
    return switch.get(lang, 'Invalid language parameter')

def get_java_command(project_name, project_dir, project_release):
     command = f"{SOURCEMETER_PATH}/Java/SourceMeterJava " \
              + f"-resultsDir={PROJECTS_DIR}/../Results/Java " \
              + f"-projectName={project_name} " \
              + f"-currentDate={project_release} " \
              + f"-projectBaseDir={project_dir} " + SOURCEMETER_JAVA_PARAMS
     return command


def get_python_command(project_name, project_dir, project_release):
    command = f"{SOURCEMETER_PATH}/Python/SourceMeterPython " \
              + f"-resultsDir={PROJECTS_DIR}/../Results/Python " \
              + f"-projectName={project_name} " \
              + f"-currentDate={project_release} " \
              + f"-projectBaseDir={project_dir} " + SOURCEMETER_PYTHON_PARAMS
    return command


def get_csharp_command(project_name, project_dir, project_release):
    command = f"{SOURCEMETER_PATH}/CSharp/SourceMeterCSharp " \
              + f"-resultsDir={PROJECTS_DIR}/../Results/CSharp " \
              + f"-projectName={project_name} " \
              + f"-currentDate={project_release} " \
              + f"-projectBaseDir={project_dir} " + SOURCEMETER_CSHARP_PARAMS
    return command

def analyze_projects(lang):
    repo_names = []
    if lang=='java':
        repo_names = parse_repo_names(JAVA_PROJECTS_LIST_FILE)
    if lang=='python':
        repo_names = parse_repo_names(PYTHON_PROJECTS_LIST_FILE)
    if lang=='csharp':
        repo_names = parse_repo_names(CSHARP_PROJECTS_LIST_FILE)

    for repo_name in repo_names:
        print('Processing repo: ' + repo_name)
        repo = get_repo(repo_name)
        cloned_repo = clone_repo(repo)
        releases = get_repo_releases(repo)
        for rel in releases:
            print(f"Processing Release: {rel.tag_name}")
            cloned_repo_tag_ref = cloned_repo.tags[rel.tag_name].commit
            cloned_repo.git.checkout(cloned_repo_tag_ref)
            repo_dir = cloned_repo.working_dir
            execute_sourcemeter(repo_name.split("/")[1],repo_dir,rel.tag_name, lang)
            print('-' * 20)



if __name__ == '__main__':
    analyze_projects('java')
    #analyze_projects('python')
    #analyze_projects('csharp')
