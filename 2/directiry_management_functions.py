import os
import shutil


def make_directory(new_folder_name, parent_directory):
    """
    create a directory if it doesn't exist
    :param new_folder_name:
    :param parent_directory:
    :return:
    """
    try:
        path = os.path.join(parent_directory, new_folder_name)
        os.mkdir(path)
    except Exception:
        pass


def remove_directory(target_folder_name, parent_directory):
    """
    remove a directory
    :param target_folder_name:
    :param parent_directory:
    :return:
    """
    try:
        path = os.path.join(parent_directory, target_folder_name)
        os.rmdir(path)
        print('DIRECTORY \"{}\" removed'.format(target_folder_name))
    except Exception:
        path = os.path.join(parent_directory, target_folder_name)
        shutil.rmtree(path)


def copy_directory(src, dst):
    """
    copy a directory from src to dst
    :param src: source path
    :param dst: destination path
    """
    shutil.copytree(src, dst, copy_function=shutil.copy)


def remove_directory_contents(directory):
    """
    removing all the contents of a directory (not THE directory!)
    :param directory: the path of the target folder
    """
    for root, dirs, files in os.walk(directory):
        for name in files:
            os.remove(os.path.join(root, name))
