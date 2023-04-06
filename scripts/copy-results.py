import os
import shutil




# Target folder containing folders with CSV files
SOURCE_MAIN_FOLDER = '/u/23/chrens1/unix/SourceMeter/ESEM/Results/Python/'
NEW_MAIN_FOLDER ='/u/23/chrens1/unix/SourceMeter/ESEM/FilteredResults/Python'

RESTRICTED_FOLDERS = ['sourcemeter','asg', 'graph', 'log', 'temp']

def copy_csv_files(new_folder_path):
    for root, dirs, files in os.walk(SOURCE_MAIN_FOLDER):

        new_dir = os.path.join(new_folder_path, os.path.relpath(root, SOURCE_MAIN_FOLDER))

        if not check_restricted_folder(new_dir):
            os.makedirs(new_dir, exist_ok=True)

            for file in files:
                if file.endswith('.csv'):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(new_dir, file)
                    #print('Will copy: '+ src_file)
                    #print('To: '+ dst_file)
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

if __name__ == '__main__':
    copy_csv_files(NEW_MAIN_FOLDER)