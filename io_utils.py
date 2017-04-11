def create_file(filename, path, data):
    """
    Creates a file entry in the given path.
    
    Raises an IOUtilException if:
        - folder name already exists in path
        - filename contains illegal characters

    :param filename: A string of the name of the file including extension
    :param path: Path to containing folder
    :param data: (possibly binary) data to be written to the file system 
    :return: None
    """
    return None


def create_new_folder(new_folder_name, path):
    """
    Creates a folder entry in the given path. Also creates path if necessary. 
    
    Raises an IOUtilException if:
        - folder name already exists in path

    :param new_folder_name: A string of the new folder name.
    :param path: Path to containing folder.
    :return: None
    """
    return None


def list_dir(path):
    """
    Returns a list of dictionaries in the following format:
    
    [{"type": "folder", "name": "sample folder", "date_added": 1490401135674, "size_bytes": -1},
    {"type": "file", "name": "sample file 1.txt", "date_added": 1490401135674, "size_bytes": 10649}]

    :param path: path to get data from
    :return: a list of dictionaries
    """
    return [{"type": "folder", "name": "sample folder", "date_added": 1490401135674, "size_bytes": -1},
            {"type": "file", "name": "sample file 1.txt", "date_added": 1490401135674, "size_bytes": 10649}]


def get_file_contents(path):
    """
    Opens a given file and returns a byte string of the data (use "rb").

    :param path: the path of the file including the filename and extension
    :return: the results of .read()
    """
    return b""


def delete_item(path):
    """
    Remove a file or folder from the filesystem. If the path is a folder, should recursively remove all files
    and folders in the path before removing the path.

    :param path: A string of a path. May contain a filename or a folder. 
    """
    pass


class IOUtilException(Exception):
    def __init__(self, *args):
        super(IOUtilException).__init__(*args)
