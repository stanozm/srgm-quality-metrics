import csv
import os

from github import Github
from datetime import datetime

# Add your Github access token here
GITHUB_URL_PREFIX = "https://github.com/"
DURATION_DATA_DIR = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data"

github = Github()


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
    releases = repo.get_releases()
    #num_releases = repo.get_releases().totalCount

    # print(repo_name + " " + str(num_releases))
    #
    # return repo_name + "\t\t\t\t\t\t\t" + str(num_releases) + "\n"

    return releases



def get_releases_for_all_repos(repo_urls):
    repos_with_releases = []

    for url in repo_urls:
        repo_name = url.removeprefix(GITHUB_URL_PREFIX)
        releases_for_repo = get_releases_for_repo(repo_name)
        repos_with_releases.append(releases_for_repo)

    return repos_with_releases


def create_release_duration_data_for_repo(repo_name, output_csv_path):
    repo = github.get_repo(repo_name)

    project_name = repo_name.split("/")[1]

    commits = repo.get_commits()
    first_commit = commits.reversed[0]
    start_time = first_commit.commit.author.date
    print('Start time:', start_time)

    results = []
    for release in repo.get_releases():
        release_time = release.published_at

        if release_time is None:
            print(f'Release time for release {release.tag_name} not found.')
            continue

        duration_weeks = (release_time - start_time).days / 7.0

        results.append((
            f'{project_name}-{release.tag_name}',
            release_time.isoformat(),
            round(duration_weeks, 2)
        ))

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Project", "release_time", "duration_weeks"])  # NEW column
        writer.writerows(results)


def create_release_duration_data_for_repo_with_custom_start(repo_name, input_file_path, output_csv_path):
    repo = github.get_repo(repo_name)
    project_name = repo_name.split("/")[1]

    custom_start = None
    custom_release_dates = {}

    with open(input_file_path, "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "project":
                continue

            if key == "custom-start":
                custom_start = datetime.strptime(value, "%d/%m/%y")
            else:
                custom_release_dates[key] = datetime.strptime(value, "%d/%m/%y")


    results = []

    for release in repo.get_releases():
        tag = release.tag_name

        if tag in custom_release_dates:
            release_time = custom_release_dates[tag]
        else:
            release_time = release.published_at
            if release_time is None:
                print(f"Release time for release {tag} not found.")
                continue

        duration_weeks = (release_time - custom_start).days / 7.0

        results.append((
            f"{project_name}-{tag}",
            release_time.isoformat(),
            round(duration_weeks, 2)
        ))

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Project", "release_time", "duration_weeks"])
        writer.writerows(results)

def init(duration_data_dir):
    global DURATION_DATA_DIR
    DURATION_DATA_DIR = duration_data_dir

if __name__ == '__main__':
    # repo_urls = parse_repo_urls(sys.argv[1])
    # # output = get_languages_for_all_repos(repo_urls)
    # output = get_releases_for_all_repos(repo_urls)
    # print(''.join(output))
    create_release_duration_data_for_repo("httpie/cli", f'{DURATION_DATA_DIR}/cli-duration.csv')
