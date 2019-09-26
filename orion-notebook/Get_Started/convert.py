import json
import logging
import os
import re
import subprocess
import time
import zipfile
from logging.handlers import TimedRotatingFileHandler
from time import strftime

logger = {}


# log file and console info showing format
def setup_logger(name, log_file, level=logging.DEBUG):
    """Function to setup log file format and output level"""
    global logger

    if logger.get(name):
        return logger.get(name)
    else:
        log = logging.getLogger(name)
        log.setLevel(logging.DEBUG)
        format_str = '%(asctime)s - %(levelname)-8s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(format_str, date_format)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)

        handler = TimedRotatingFileHandler(log_file, when='W0', backupCount=0)
        handler.suffix = "%Y%m%d"

        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(filename)s - %(lineno)d - %(message)s',
                                      date_format)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logging.getLogger(name)


def remove_empty_lines(filename):
    with open(filename) as file_handle:
        lines = file_handle.readlines()

    with open(filename, 'w') as file_handle:
        lines = filter(lambda x: x.strip(), lines)
        file_handle.writelines(lines)


def rw_file(filename, **kwargs):
    try:
        for k, v in kwargs.items():
            with open(filename, "r+") as fp:
                lines = [line.replace(line[:], "".join([v, "\n"]))
                         if "".join([k, "=="]) in line.lower() else line for line in fp]
                fp.seek(0)
                fp.truncate()
                fp.writelines(lines)
    except Exception as e:
        e_message = "Failed in I/O with log file: {} \n".format(e)
        logger.error(e_message)
        raise RuntimeError(e_message)


def zip_folder(folder_path, output_path):
    base_dir = os.path.abspath(folder_path)
    try:
        with zipfile.ZipFile(output_path, "w",
                             compression=zipfile.ZIP_DEFLATED) as zf:
            base_path = os.path.normpath(base_dir)
            for dirpath, dirnames, filenames in os.walk(base_dir):
                dirnames[:] = [d for d in dirnames if not d[0] == '.'
                               and "__pycache__" not in dirnames
                               and "venv" not in dirnames]
                for dir_name in sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, dir_name))
                    zf.write(path, os.path.relpath(path, base_path))

                filenames = [f for f in filenames if not f[0] == '.']
                for f_name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, f_name))
                    if os.path.isfile(path):
                        filename, file_extension = os.path.splitext(f_name)
                        if str(file_extension) != ".ipynb":
                            zf.write(path, os.path.relpath(path, base_path))
    except Exception as e:
        e_message = "Zipping project folder failed: {} \n".format(e)
        logger.error(e_message)
        raise RuntimeError(e_message)
    finally:
        zf.close()


def validate_input(project_root, convert_file_path, output_directory='', data_url='', data_dir=''):
    # check project path
    try:
        check_project_path(project_root)
    except Exception:
        raise
    else:
        # check exec_file
        if convert_file_path.split('.')[-1] == "ipynb":
            path_exec_file_py = convert_file_path[:-6] + '.py'
        else:
            path_exec_file_py = convert_file_path
        try:
            check_file_path(convert_file_path, path_exec_file_py, project_root)
        except Exception:
            raise
        else:
            # check output path
            path_output_dir = output_directory
            try:
                check_output_path(path_output_dir, project_root)
            except Exception:
                raise
            else:
                # check data url
                try:
                    check_data_url(data_url)
                except Exception:
                    raise
                else:
                    # check data dir
                    try:
                        check_data_path(data_dir, project_root)
                    except Exception:
                        raise


def get_files(folder, ext='.ipynb'):
    file_list = list()
    for root_dir, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root_dir, f))
        return file_list


def convert2py(folder):
    """
    Convert Notebook '.ipynb' files to python3 '.py' files.
    """

    try:
        files = get_files(os.path.abspath(folder))

        for i, file in enumerate(files):
            try:
                with open(log_path, 'a+') as outfile:
                    subprocess.check_output(["jupyter", "nbconvert", "--to", "python", file],
                                            stderr=outfile, universal_newlines=True)

            except subprocess.CalledProcessError as err:
                return_code = err.returncode
                # output = err.output
                error_msg = "Error: during converting {} file to python'.py' file. {}{}\n".format(
                    file, return_code, err)
                logger.error(error_msg)
                raise RuntimeError

        txt = 'Validated files successfully! \n'
        logger.info(txt)
    except Exception:
        raise RuntimeError


def check_project_path(dirname):
    dir_path = os.path.abspath(dirname)
    if not os.path.isdir(dir_path) or not dir_path.startswith(path_home):

        e_message = "'project_root' does not exist or it is NOT inside '{}' directory " \
                    "[Notebook HOME directory]. \n".format(path_home)
        logger.error(e_message)
        err = "Error: conversion failed, please refer to '{}' for details. \n".format(
            os.path.relpath(log_path, path_home))
        logger.error(err)
        raise RuntimeError
    else:
        try:
            convert2py(dir_path)
        except Exception:
            # err = "Error: conversion failed, please refer to '{}' for details. \n".format(
            #     os.path.relpath(log_path, path_home))
            # logger.error(err)
            raise


def check_file_path(exe_file_path, path_exec_file_py, workspace_dir):
    file_path = os.path.abspath(path_exec_file_py)
    file_extension = os.path.splitext(file_path)[1]
    if not file_path.startswith(os.path.abspath(workspace_dir)):
        e_message = "The 'main_file' is NOT inside the project root directory. \n"
        logger.error(e_message)
        err = "conversion failed: please refer to '{}' for details. \n".format(
            os.path.relpath(log_path, path_home))
        logger.error(err)
        raise RuntimeError
    else:
        if os.path.isfile(file_path) or os.path.isfile(exe_file_path):
            if not (file_extension == ".py" or file_extension == ".ipynb"):
                e_message = "The 'main_file' is Neither a '.py' file Nor an '.ipynb' file. \n"
                logger.error(e_message)
                err = "conversion failed: please refer to '{}' for details. \n".format(
                    os.path.relpath(log_path, path_home))
                logger.error(err)
                raise RuntimeError
        else:
            e_message = "The 'main_file' to be converted does NOT exist. \n"
            logger.error(e_message)
            err = "Error: conversion failed, please refer to '{}' for details. \n".format(
                os.path.relpath(log_path, path_home))
            logger.error(err)
            raise RuntimeError


def check_output_path(dirname, workspace_dir=''):
    dir_path = dirname
    if dir_path == "":
        msg = "Warning: 'output_directory' is empty, no result files will be output. \n"
        logger.info(msg)
    else:
        dir_path = os.path.abspath(dir_path)
        try:
            os.makedirs(dir_path)
        except FileExistsError:
            pass
        if not dir_path.startswith(os.path.abspath(workspace_dir) + os.sep):
            e_message = "The 'output_directory' is NOT inside the' project_root' directory. \n"
            logger.error(e_message)
            err = "Error: conversion failed, please refer to '{}' for details. \n".format(
                os.path.relpath(log_path, path_home))
            logger.error(err)
            raise RuntimeError


def check_data_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if url != '':
        if not re.match(regex, url):
            e_message = "Invalid 'data_url'! \n"
            logger.error(e_message)
            raise RuntimeError


def check_data_path(dirname, workspace_dir=''):
    dir_path = dirname
    if dir_path != '':
        dir_path = os.path.abspath(dir_path)
        if not dir_path == "":
            try:
                os.makedirs(dir_path)
            except FileExistsError:
                pass
            if not dir_path.startswith(os.path.abspath(workspace_dir) + os.sep):
                e_message = "The 'data_dir' is NOT inside the 'project_root' directory. \n"
                logger.error(e_message)
                # err = "Error: conversion failed, please refer to '{}' for details. \n".format(
                #     os.path.relpath(log_path, path_home))
                # logger.error(err)
                raise RuntimeError


def get_time():
    cur_time = strftime("%Y-%m-%dT%H:%M")
    return cur_time


def write_to_disk(logger_path, project_root, convert_file_path, output_directory, data_url, data_dir):
    data = open(logger_path, 'a')
    timestamp = get_time()
    data.write('DateTime={}, project root={}, convert file={}, output directory={} data_url={} data_dir={} \n\n'.format(
        timestamp, project_root, convert_file_path, output_directory, data_url, data_dir))
    data.close()


def convert2or(workspace_dir, output_path, exec_file_name, data_uri="", data_path=""):
    """
        Wrap and convert python3 '.py' files into an file that can be uploaded
        as a task by NBAI Cloud Platform.
    """
    try:
        entry_filename = os.path.splitext(os.path.basename(exec_file_name))[0]
    except Exception as e:
        err = 'Invalid arguments, {}. \n'.format(e)
        logger.error(err)
        raise RuntimeError(err)
    else:
        # Generate requirements.txt
        try:
            p = subprocess.Popen(["pipreqs", "--force", workspace_dir])
            p.wait()
            time.sleep(2)

            # fix the bug raising from 'tensorflow', 'tensorflow_gpu'
            filename = os.path.join(workspace_dir, "requirements.txt")

            rw_file(filename, matplotlib="matplotlib", tensorflow_gpu="", tensorflow="tensorflow-gpu")
            remove_empty_lines(filename)
            txt = "Generated 'requirements.txt' successfully! \n"
            logger.info(txt)

        except Exception as e:
            err = "Generating 'requirements.txt' failed: {}. \n".format(e)
            logger.error(err)
            # err = "Error: conversion failed, please refer to '{}' for details. \n".format(
            #     os.path.relpath(log_path, path_home))
            # logger.error(err)
            raise RuntimeError(err)
        else:
            # Generate params.json
            try:
                exec_file_name_v = os.path.relpath(exec_file_name, start=workspace_dir)
                data_path_v = "" if data_path == "" else os.path.relpath(data_path, start=workspace_dir)
                output_path_v = "" if output_path == "" else os.path.relpath(output_path, start=workspace_dir)
                params_json = json.dumps({"exec_file_name": exec_file_name_v,
                                          "data_uri": data_uri,
                                          "data_path": data_path_v,
                                          "output_path": output_path_v,
                                          })
                with open(os.path.join(workspace_dir, "params.json"), 'w+') as f:
                    f.write(params_json)
                txt = "Generated 'params.json' successfully! \n"
                logger.info(txt)

            except Exception as e:
                err = "Generating 'params.json' failed: {} \n".format(e)
                logger.error(err)
                # err = "Error: conversion failed, please refer to '{}' for details. \n".format(
                #     os.path.relpath(log_path, path_home))
                # logger.error(err)
                raise RuntimeError(err)

            else:
                time.sleep(2)
                try:
                    zip_folder_path = os.path.join(workspace_dir, os.pardir, "NBAI_task_files")

                    if not os.path.exists(zip_folder_path):
                        os.makedirs(zip_folder_path)

                    output_filename = str(entry_filename) + "_cloud.zip"
                    zip_folder(workspace_dir, os.path.join(zip_folder_path, output_filename))
                    txt1 = "Zipped files successfully! \n"
                    logger.info(txt1)
                    txt2 = "Files have been converted successfully! \n"
                    logger.info(txt2)
                    txt3 = "This task is saved in: {}. \n".format(
                        os.path.normpath(
                            os.path.relpath(os.path.join(zip_folder_path, output_filename), start=path_home)))
                    logger.info(txt3)

                except Exception as e:
                    err = "Zipping files failed: {}. \n".format(e)
                    logger.error(err)
                    # err = "Error: conversion failed, please refer to '{}' for details. \n".format(
                    #     os.path.relpath(log_path, path_home))
                    # logger.error(err)
                    raise RuntimeError(err)
                else:
                    try:
                        os.remove(os.path.join(workspace_dir, "params.json"))
                        os.remove(os.path.join(workspace_dir, "requirements.txt"))
                    except Exception as e:
                        err = 'Removing files failed: {}. \n'.format(e)
                        logger.error(err)


def main(project_root, convert_file_path, output_directory, data_url, data_dir):
    if project_root == "":
        err = "'project_root' is required. \n"
        logger.error(err)
        e = "Error: conversion failed, please refer to '{}' for details. \n".format(
            os.path.relpath(log_path, path_home))
        logger.error(e)
        raise RuntimeError

    if convert_file_path == "":
        err = "'main_file' is required. \n"
        logger.error(err)
        e = "Error: conversion failed, please refer to '{}' for details. \n".format(
            os.path.relpath(log_path, path_home))
        logger.error(e)
        raise RuntimeError

    project_root = os.path.join(path_home, project_root) if not os.path.isabs(project_root) else project_root
    convert_file_path = os.path.join(path_home, convert_file_path) if not os.path.isabs(
        convert_file_path) else convert_file_path

    if not output_directory == "":
        output_directory = os.path.join(path_home, output_directory) if not os.path.isabs(output_directory) \
            else output_directory

    if not data_dir == "":
        data_dir = os.path.join(path_home, data_dir) if not os.path.isabs(data_dir) else data_dir
    try:
        validate_input(project_root, convert_file_path, output_directory, data_url, data_dir)
    except Exception:
        e_message = "Error: conversion failed, please refer to '{}' for details. \n".format(
            os.path.relpath(log_path, path_home))
        logger.error(e_message)
        raise
    else:
        try:
            convert_file_path_abs = os.path.abspath(convert_file_path)
            py_convert_file = os.path.splitext(convert_file_path_abs)[0] + '.py'

            convert2or(project_root, output_directory, py_convert_file, data_url, data_dir)
            write_to_disk(log_path, project_root, py_convert_file, output_directory, data_url, data_dir)
        except Exception:
            e_message = "Error: conversion failed, please refer to '{}' for details. \n'".format(
                os.path.relpath(log_path, path_home))
            logger.error(e_message)
            raise


# config paths
path_home = os.path.join(os.environ['HOME'], 'sync')
log_dir = os.path.join(path_home, "NBAIlog")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except FileExistsError:
        pass

log_path = os.path.join(log_dir, "NBAIlog.log")
logger = setup_logger("NBAIlog", log_path)
