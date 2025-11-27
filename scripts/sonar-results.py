import requests
import math
import pandas as pd

JAVA_PROJECTS_LIST_FILE = 'inputs/projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = 'inputs/projects-python-test.txt'
CSHARP_PROJECTS_LIST_FILE = 'inputs/projects-csharp-test.txt'

PROJECTS_DIR = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/Sonarqube"
JAVA_BUILD_TYPES_FILE = 'inputs/projects-java-build.txt'
JAVA_BUILD_TYPE_DICT = {}

SONAR_PLUGIN = 'id "org.sonarqube" version "3.5.0.2730"'
# SONAR_TOKEN = 'sqa_fd21d6bd9bf0f60af5e343e06ce59467c4b2f90b'
SONAR_TOKEN = "squ_f1bbe99990d85fd6548fb88e81cda2babacc7e97"
SONAR_URL = 'http://localhost:9000'


def get_all_metrics() -> list:
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    url = f"{SONAR_URL}/api/metrics/search"

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    metrics = [m["key"] for m in resp.json().get("metrics", [])]
    return metrics


def get_all_projects() -> list:
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    projects = []
    page = 1

    while True:
        url = f"{SONAR_URL}/api/projects/search"
        resp = requests.get(url, headers=headers, params={"p": page, "ps": 500})
        resp.raise_for_status()

        data = resp.json()
        projects.extend(data.get("components", []))

        paging = data["paging"]
        total_pages = math.ceil(paging["total"] / paging["pageSize"])

        if page >= total_pages:
            break

        page += 1

    return projects

def get_project_metrics(project_key: str, metric_keys: list):
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    url = f"{SONAR_URL}/api/measures/component"
    params = {
        "component": project_key,
        "metricKeys": ",".join(metric_keys)
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    data = resp.json().get("component", {})
    measures = data.get("measures", [])

    metric_map = {m["metric"]: m.get("value") for m in measures}

    return metric_map

def export_all_project_metrics():

    print("Getting all metric types...")
    metrics = get_all_metrics()

    print("Getting all projects...")
    projects = get_all_projects()

    print(f"Found {len(projects)} projects and {len(metrics)} metrics.")

    results = []

    for proj in projects:
        key = proj["key"]
        name = proj.get("name", "")

        metric_values = get_project_metrics(key, metrics)

        results.append({
            "project_key": key,
            "project_name": name,
            **metric_values
        })

    return results

if __name__ == '__main__':
    # metrics = get_all_metrics()
    # projects = get_all_projects()
    # print(metrics)
    #
    # print(projects)

    # headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    # r = requests.get("http://localhost:9000/api/projects/search", headers=headers)
    # print(r.json())

    results =  export_all_project_metrics()
    pd.DataFrame(results).to_csv(f"{PROJECTS_DIR }/sonarqube_metrics.csv", index=False)







