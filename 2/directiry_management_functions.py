import os
import shutil


def make_directory(new_folder_name, parent_directory):
    try:
        path = os.path.join(parent_directory, new_folder_name)
        os.mkdir(path)
        print('DIRECTORY \"{}\" CREATED'.format(new_folder_name))
    except Exception as e:
        pass


def remove_directory(target_folder_name, parent_directory):
    try:
        path = os.path.join(parent_directory, target_folder_name)
        os.rmdir(path)
        print('DIRECTORY \"{}\" removed'.format(target_folder_name))
    except Exception as e:
        # print(e)
        shutil.rmtree(path)

def copy_directory(src, dst):
    shutil.copytree(src, dst, copy_function=shutil.copy)
