import sourcemeter_analyzer as sm_analyzer
import copy_sourcemeter_results as csmr
import sonar_analyzer as sonar_analyzer
import sonar_results as sonar_results
import strait_data_processing as strait
import github_repo_miner as repo_miner
import all_data_merge as merger


PROJECT_NAME = "Significant-Gravitas/AutoGPT"
REPO_NAME = PROJECT_NAME.split("/")[-1]
PROJECTS_DIR = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/AutoGPT/"


SOURCEMETER_PROJECTS_DIR = f"{PROJECTS_DIR}/Sourcemeter"
SONARQUBE_PROJECTS_DIR = f"{PROJECTS_DIR}/Sonarqube"
STRAIT_PROJECTS_DIR = f"{PROJECTS_DIR}/STRAIT"
DURATION_DATA_DIR = f"{PROJECTS_DIR}/Duration"






if __name__ == '__main__':
    print("STAGE 1a: Executing sourcemeter analysis")
    sm_analyzer.init(SOURCEMETER_PROJECTS_DIR)
    sm_analyzer.analyze_projects("python")
    print("--------------------------------------------------------------------")

    print("STAGE 1b: Copying sourcemeter results")
    csmr.init(F"{PROJECTS_DIR}/Results/Python", f'{PROJECTS_DIR}/FilteredResults/')
    csmr.copy_csv_files()
    csmr.generate_summaries()
    print("--------------------------------------------------------------------")

    print("STAGE 2a: Executing Sonarqube analysis")
    sonar_analyzer.init(SONARQUBE_PROJECTS_DIR)
    sonar_analyzer.analyze_projects("python")
    print("--------------------------------------------------------------------")

    print("STAGE 2b: Exporting Sonarqube results")
    sonar_results.init(SONARQUBE_PROJECTS_DIR)
    sonar_results.export_all_project_metrics()
    print("--------------------------------------------------------------------")

    print("STAGE 3: Processing STRAIT results")
    strait.init(STRAIT_PROJECTS_DIR)
    strait.create_strait_summaries()
    print("--------------------------------------------------------------------")

    print("STAGE 4: Creating project duration data")
    repo_miner.init(DURATION_DATA_DIR)
    repo_miner.create_release_duration_data_for_repo(PROJECT_NAME, f'{DURATION_DATA_DIR}/{REPO_NAME}-duration.csv')
    print("--------------------------------------------------------------------")

    print("STAGE 5: Merging all results")
    merger.merge_strait_sonar_sourcemeter(f'{PROJECTS_DIR}',
                                        f'{STRAIT_PROJECTS_DIR}/STRAIT-{REPO_NAME}-Summary.csv',
                                          f'{SONARQUBE_PROJECTS_DIR}/sonarqube_metrics.csv',
                                          f'{PROJECTS_DIR}/FilteredResults/{REPO_NAME}/{REPO_NAME}-Summary.csv',
                                          f'{DURATION_DATA_DIR}/{REPO_NAME}-duration.csv',)
    print("--------------------------------------------------------------------")