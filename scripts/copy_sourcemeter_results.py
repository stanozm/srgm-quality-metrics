import os
import shutil
import pandas as pd
import numpy as np




# Target folder containing folders with CSV files
SOURCE_MAIN_FOLDER = '/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/Results/Python/'
NEW_MAIN_FOLDER ='/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/Results/FilteredResults/Python'

RESTRICTED_FOLDERS = ['sourcemeter','asg', 'graph', 'log', 'temp', 'analyzer']

# def copy_csv_files(new_folder_path):
#     for root, dirs, files in os.walk(SOURCE_MAIN_FOLDER):
#
#         new_dir = os.path.join(new_folder_path, os.path.relpath(root, SOURCE_MAIN_FOLDER))
#
#         if not check_restricted_folder(new_dir):
#             os.makedirs(new_dir, exist_ok=True)
#
#             for file in files:
#                 if (file.endswith('.csv')
#                         and "-CloneClass" not in file)\
#                         and "-CloneInstance" not in file\
#                         and "-Attribute" not in file\
#                         and "-Folder" not in file\
#                         and "-Module" not in file\
#                         and "-Component" not in file:
#                     src_file = os.path.join(root, file)
#                     dst_file = os.path.join(new_dir, file)
#                     #print('Will copy: '+ src_file)
#                     #print('To: '+ dst_file)
#                     shutil.copy(src_file, dst_file)

def copy_csv_files():
    for root, dirs, files in os.walk(SOURCE_MAIN_FOLDER):

        rel_path = os.path.relpath(root, SOURCE_MAIN_FOLDER)

        parts = rel_path.split(os.sep)

        if "python" in parts:
            python_index = parts.index("python")
            parts.pop(python_index)


        cleaned_rel_path = os.sep.join(parts)

        new_dir = os.path.join(NEW_MAIN_FOLDER, cleaned_rel_path)


        if not check_restricted_folder(new_dir):
            os.makedirs(new_dir, exist_ok=True)

            for file in files:
                if (file.endswith('.csv')
                        and "-CloneClass" not in file
                        and "-CloneInstance" not in file
                        and "-Attribute" not in file
                        and "-Folder" not in file
                        and "-Module" not in file
                        and "-Component" not in file):

                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(new_dir, file)
                    shutil.copy(src_file, dst_file)

def check_restricted_folder(folder_to_check):
    for folder_name in RESTRICTED_FOLDERS:
        if folder_name in folder_to_check:
            return True
    return False

def list_project_dirs(target_folder):
    folder_list = []
    for directory in os.listdir(target_folder):
        if os.path.isdir(os.path.join(target_folder, directory)):
            folder_list.append(directory)
    return folder_list





def generate_summaries():
    METRICS = {"CBO", "DIT", "LCOM5", "LLOC", "LOC", "NLM", "NM", "NOA",
               "NOC", "NOD", "NOI", "NOP", "NOS", "RFC", "WMC",
               "McCC", "NUMPAR"}

    print("Generating summaries")

    for project in os.listdir(NEW_MAIN_FOLDER):
        print("Processing ", project)
        project_path = os.path.join(NEW_MAIN_FOLDER, project)
        if not os.path.isdir(project_path):
            continue

        project_summary_rows = []


        for version in os.listdir(project_path):
            print("Processing version", f"{project}-{version}")
            version_path = os.path.join(project_path, version)
            if not os.path.isdir(version_path):
                continue

            version_summary_filename = f"{project}-{version}-Summary.csv"
            version_summary_path = os.path.join(version_path, version_summary_filename)


            if not os.path.exists(version_summary_path):
                summary_data = {}


                for fname in os.listdir(version_path):
                    if not fname.endswith(".csv"):
                        continue


                    if not fname.startswith(project + "-"):
                        continue

                    parts = fname.split("-")
                    if len(parts) < 2:
                        continue

                    TYPE = parts[-1].replace(".csv", "")

                    csv_path = os.path.join(version_path, fname)


                    df = pd.read_csv(csv_path)



                    for col in df.columns:
                        print("processing column ", col)
                        if col in METRICS:
                            avg_value = df[col].mean()
                            med_value = df[col].median()
                            std_value = df[col].std()
                            p95_value = df[col].quantile(0.95)

                            print(f'Values for {col}: {df[col]}')
                            print(f'Avergage Value: {avg_value}')
                            print(f'Median Value: {med_value}')
                            print(f'Standard Deviation: {std_value}')
                            print(f'P-Value: {p95_value}')


                            summary_data[f"{col}-{TYPE}-Avg"] = avg_value
                            summary_data[f"{col}-{TYPE}-Median"] = med_value
                            summary_data[f"{col}-{TYPE}-Std"] = std_value
                            summary_data[f"{col}-{TYPE}-P95"] = p95_value

                pd.DataFrame([summary_data]).to_csv(version_summary_path, index=False)


            version_df = pd.read_csv(version_summary_path)
            version_df.insert(0, "Project", f"{project}-{version}")
            project_summary_rows.append(version_df)


        if project_summary_rows:
            project_summary_df = pd.concat(project_summary_rows, ignore_index=True)

            project_summary_df.sort_values(by="Project", inplace=True)

            project_summary_path = os.path.join(project_path, f"{project}-Summary.csv")
            project_summary_df.to_csv(project_summary_path, index=False)

    print("All summaries generated successfully.")

def init(projects_dir_path, new_dir_path):
    global SOURCE_MAIN_FOLDER
    global NEW_MAIN_FOLDER
    SOURCE_MAIN_FOLDER = projects_dir_path
    NEW_MAIN_FOLDER = new_dir_path


if __name__ == '__main__':
    copy_csv_files()
    generate_summaries()