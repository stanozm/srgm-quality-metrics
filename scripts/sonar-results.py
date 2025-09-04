import requests
import csv

JAVA_PROJECTS_LIST_FILE = 'inputs/projects-java-test.txt'
PYTHON_PROJECTS_LIST_FILE = 'inputs/projects-python-test.txt'
CSHARP_PROJECTS_LIST_FILE = 'inputs/projects-csharp-test.txt'

PROJECTS_DIR = "/u/23/chrens1/unix/Sonar/ESEM/projects"
JAVA_BUILD_TYPES_FILE = 'inputs/projects-java-build.txt'
JAVA_BUILD_TYPE_DICT = {}

SONAR_PLUGIN = 'id "org.sonarqube" version "3.5.0.2730"'
SONAR_TOKEN = 'squ_2b538bab99a18a124554d34ccc4a97702ffe9ca2'
SONAR_URL = 'http://localhost:9000'



def get_all_projects():
    projects = []
    page = 1
    page_size = 100
    auth = (SONAR_TOKEN, "")

    while True:
        response = requests.get(
            f"{SONAR_URL}/api/projects/search",
            params={"p": page, "ps": page_size},
            auth=auth
        )
        response.raise_for_status()
        data = response.json()
        projects.extend(data.get("components", []))
        if page * page_size >= data["paging"]["total"]:
            break
        page += 1
    return projects

def get_all_metric_types():

    metrics = []
    page = 1
    page_size = 500
    auth = (SONAR_TOKEN, "")

    while True:
        response = requests.get(
            f"{SONAR_URL}/api/metrics/search",
            params={"p": page, "ps": page_size},
            auth=auth
        )
        response.raise_for_status()
        data = response.json()
        metrics.extend([m["key"] for m in data.get("metrics", [])])
        if page * page_size >= data["total"]:
            break
        page += 1
    return metrics

def get_metric_values_for_project(project_key, metrics_types):
    auth = (SONAR_TOKEN, "")
    response = requests.get(
        f"{SONAR_URL}/api/measures/search",
        params={"project": project_key, "metricKeys": ",".join(metrics_types)},
        auth=auth
    )
    response.raise_for_status()
    data = response.json()
    measures = {m["metric"]: m.get("value", "") for m in data.get("measures", [])}
    return measures

def export_metrics_csv(projects, metrics, output_file="metrics.csv"):

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["projectKey", "projectName"] + metrics
        writer.writerow(header)

        for project in projects:
            project_key = project["key"]
            project_name = project["name"]
            measures = fetch_metrics_for_project(project_key, metrics)
            row = [project_key, project_name] + [measures.get(m, "") for m in metrics]
            writer.writerow(row)

    print(f"Metrics exported successfully to {output_file}")



if __name__ == '__main__':
    projects = get_all_projects()
    metric_types = get_all_metric_types()








