import sys
from github import Github

import git

TOKEN="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"
SOURCEMETER_PATH = "/u/23/chrens1/unix/utility/SourceMeter/SourceMeter-10.0.0-x64-linux/SourceMeter-10.0.0-x64-Linux/Java/"
SOURCEMETER_PARAMS = "-resultsDir=Results -runFB=false -runAndroidHunter=false -runVulnerabilityHunter=false -runFaultHunter=false -runRTEHunter=false -runDCF=false -runMetricHunter=false -runMET=true -runUDM=false -runPMD=false -runSQ=false  -runLIM2Patterns=false"
PROJECTS_DIR = SOURCEMETER_PATH + "/ESEM"

github = Github(TOKEN)


def parse_repo_names(path_to_repos_file):
    with open(path_to_repos_file) as inputFile:
        repos_list = inputFile.read().splitlines()
    return repos_list


def get_repo(repo_name):
    repo = github.get_repo(repo_name)
    return repo

def clone_repo(github_repo):
    repo_dir = github_repo.name
    git.Repo.clone_from(github_repo.git_url.replace("git://", "https://"), f'./{repo_dir}')
    return repo_dir



def get_repo_releases(github_repo):
    releases = github_repo.get_releases()
    return releases


if __name__ == '__main__':
    repo_names = parse_repo_names(sys.argv[1])

    for repo_name in repo_names:
        print('Processing repo: ' + repo_name)
        repo = get_repo(repo_name)
        clone_repo(repo)
        releases = get_repo_releases(repo)
        for rel in releases:
            print(f"Release Name: {rel.title}")
            print(f"Tag Name: {rel.tag_name}")
            print('-' * 20)

    print(repo_names)
