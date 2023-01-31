''' some functions in here '''

import os
import shutil
import stat
import logging
from datetime import datetime

###################################################################################################

def del_rw(action, name, exc):
    ''' Removes read protection and removes a file'''
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

###################################################################################################

def delete_dir(directory: str):
    '''  Remove everything in dir '''

    sub_dirs = os.scandir(directory)
    for sub_dir in sub_dirs:
        if sub_dir.is_dir():
            shutil.rmtree(sub_dir.path, onerror=del_rw)
        elif sub_dir.is_file() or sub_dir.is_symlink():
            os.unlink(sub_dir.path)

###################################################################################################

def setup_logger():
    ''' setups the logging feature '''

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Setup format, filename and logging level
    logging_format = '%(asctime)s %(levelname)s:%(message)s'
    logging_file_name = 'gtm_ims_syncher_'
    logging_file_name += datetime.now(tz=None).strftime('%d_%m_%Y_%H_%M_%S') + '.log'
    logging.basicConfig(filename=logging_file_name, encoding='utf-8', format=logging_format,
        level=logging.INFO)

###################################################################################################

def setup_temporary_working_folders(source_dir: str, target_dir: str):
    ''' set ups temporary working folder to checkout code or commit code to the repositories'''

    # create temporary source working directory
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    else:
        delete_dir(source_dir)

    # create temporary target working directory
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    else:
        delete_dir(target_dir)
