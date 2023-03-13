import sys

from github import Github

# Add your Github access token here
TOKEN = "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"
GITHUB_URL_PREFIX = "https://github.com/"

github = Github(TOKEN)


def parse_repo_urls(path_to_url_file):
    with open(path_to_url_file) as inputFile:
        url_list = inputFile.read().splitlines()
    return url_list


def get_languages_for_repo(repo_name):

    repo = github.get_repo(repo_name)

    languages = repo.get_languages()

    total_size = sum(list(languages.values()))

    result = []

    for lang, size in languages.items():
        result.append(lang + ":" + str(round(size / total_size * 100, 2)) + "% ")

    return repo_name + "\t\t\t\t\t" + str(result) + "\n"


def get_languages_for_all_repos(repo_urls):
    repos_with_languages = []

    for url in repo_urls:
        repo_name = url.removeprefix(GITHUB_URL_PREFIX)
        languages_for_repo = get_languages_for_repo(repo_name)
        repos_with_languages.append(languages_for_repo)

    return repos_with_languages

def get_releases_for_repo(repo_name):
    repo = github.get_repo(repo_name)
    num_releases = repo.get_releases().totalCount
    print(repo_name + " " + str(num_releases))

    return repo_name + "\t\t\t\t\t\t\t" + str(num_releases) + "\n"

def get_releases_for_all_repos(repo_urls):
    repos_with_releases = []

    for url in repo_urls:
        repo_name = url.removeprefix(GITHUB_URL_PREFIX)
        releases_for_repo = get_releases_for_repo(repo_name)
        repos_with_releases.append(releases_for_repo)

    return repos_with_releases







if __name__ == '__main__':
    repo_urls = parse_repo_urls(sys.argv[1])
    # output = get_languages_for_all_repos(repo_urls)
    output = get_releases_for_all_repos(repo_urls)
    print(''.join(output))
