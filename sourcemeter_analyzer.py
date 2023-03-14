import sys
import subprocess as sp, shlex
from github import Github

import git


SOURCEMETER_PATH = "/utility/SourceMeter/SourceMeter-10.0.0-x64-linux/SourceMeter-10.0.0-x64-Linux/Java"
SOURCEMETER_PARAMS = " -runFB=false" \
                     " -runAndroidHunter=false" \
                     " -runVulnerabilityHunter=false" \
                     " -runFaultHunter=false" \
                     " -runRTEHunter=false" \
                     " -runDCF=false" \
                     " -runMetricHunter=false" \
                     " -runMET=false"
PROJECTS_DIR =  "/u/23/chrens1/unix/utility/SourceMeter/SourceMeter-10.0.0-x64-linux/SourceMeter-10.0.0-x64-Linux/Java/ESEM"

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

def execute_sourcemeter(project_name, project_dir, project_release):
    command = f".{SOURCEMETER_PATH}/SourceMeterJava " \
              + f"-projectName={project_name}-{project_release} " \
              + f"-projectBaseDir={project_dir} " + f"-resultsDir={PROJECTS_DIR}/Results " + SOURCEMETER_PARAMS
    print('Executing command: ' + command)
    sp.run(shlex.split(command), shell=True)



if __name__ == '__main__':
    repo_names = parse_repo_names(sys.argv[1])

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
            execute_sourcemeter(repo_name.split("/")[1],repo_dir,rel.tag_name)
            print('-' * 20)

    print(repo_names)
