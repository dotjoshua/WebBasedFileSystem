import random
import sqlite3


def create_file(filename, path, data):
    """
    Creates a file entry in the given path.
    
    Raises an IOUtilException if:
        - filename already exists in path
        - filename contains illegal characters

    :param filename: A string of the name of the file including extension
    :param path: Path to containing folder
    :param data: (possibly binary) data to be written to the file system 
    :return: None
    """

    try:
        conn = sqlite3.connect("db/database.sqlt")
        c = conn.cursor()
        d = conn.cursor()

        selectStatement = "SELECT file_name from file WHERE file_path = %s AND file_name =  %s AND file_type = 'file';"
        selectData = (path, filename)
        c.execute(selectStatement,selectData)
        fileList = c.fetchall()
        if(len(fileList) == 0):
            statement = "INSERT INTO file (file_type, file_name, file_path,file_data, file_size) values (%s,%s,%s,%s,%s)"
            data = ("file", filename, path,data,len(data))
            d.execute(statement,data)
            conn.commit()
        else:
            raise IOUtilException("File Already Exists")
    except:
        print("Can not connect to database")

    conn.close()
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

    try:
        conn = sqlite3.connect("db/database.sqlt")
        c = conn.cursor()
        d = conn.cursor()

        selectStatement = "SELECT file_name from file WHERE file_path = %s AND file_name =  %s AND file_type = 'folder';"
        selectData = (path, new_folder_name)
        c.execute(selectStatement,selectData)
        fileList = c.fetchall()

        if(len(fileList) == 0):
            statement = "INSERT INTO file (file_type, file_name, file_path) values (%s,%s,%s)"
            data = ("folder", new_folder_name, path)
            d.execute(statement,data)
            conn.commit()
        else:
            raise IOUtilException("Folder Already Exists")
    except:
        print("Can not connect to database")

    conn.close()
    return None


def list_dir(path):
    """
    Returns a list of dictionaries in the following format:
    
    [{"type": "folder", "name": "sample folder", "date_added": 1490401135674, "size_bytes": -1},
    {"type": "file", "name": "sample file 1.txt", "date_added": 1490401135674, "size_bytes": 10649}]

    :param path: path to get data from
    :return: a list of dictionaries
    """
    fileList = []
    try:
        conn = sqlite3.connect("db/database.sqlt")
        c = conn.cursor()
        statement = "SELECT * FROM file WHERE file_path = %s;"
        data = (path,)
        c.execute(statement,data)
        aList = c.fetchall()

        for file in aList:
            fileList.append({"type":file[1],"name":file[2],"date_added":file[4],"size_bytes":file[6]})

    except:
        print("Can not connect to database")

    conn.close()
    return fileList

        #[{"type": "folder", "name": "sample folder", "date_added": 1490401135674, "size_bytes": -1},
            #{"type": "file", "name": "sample file 1.txt", "date_added": 1490401135674, "size_bytes": 10649}]


def get_file_contents_location(path):
    """
    Opens a given file and returns the name of the actual file on disk.

    :param path: the path of the file including the filename and extension
    :return: a string of the true file
    """
    return ["SAMP-LEJP-G93R-DH3E", "SAMP-LETX-TMDH-93JW", "SAMP-LEPD-FWLE-2E2H"][random.randint(0, 2)]


def delete_item(path):
    """
    Remove a file or folder from the filesystem. If the path is a folder, should recursively remove all files
    and folders in the path before removing the path.

    :param path: A string of a path. May contain a filename or a folder. 
    :return: None
    """
    try:
        conn = sqlite3.connect("db/database.sqlt")
        c = conn.cursor()
        d = conn.cursor()
        statement = "SELECT * FROM file WHERE file_path = %s;"
        data = (path,)
        c.execute(statement,data)
        aList = c.fetchall();
        for file in aList:
            if(file[1] == "file"):
                deleteStatement = "DELETE FROM file WHERE file_name = %s AND file_type = 'file';"
                deleteData = (file[2])
                d.execute(deleteStatement,deleteData)
            else:
                #recursive call to delete everything in the folder we are trying to delete
                delete_item(path + "/" + file[2])
                deleteStatement = "DELETE FROM file WHERE file_name = %s AND file_type = 'folder';"
                deleteData = (file[2])
                d.execute(deleteStatement, deleteData)
    except:
        print("Can not connect to database")

    conn.close()

    return None


def search(search_query):
    """
    Searches the index table and returns 1-10 results.
    
     Raises an IOUtilException if:
        - no results were found

    :param search_query: a string of the user's search query.
    :return: a list of the full paths of 1-10 items. 
    """

    pathList = []
    if len(search_query) < 4:
        raise IOUtilException("query too short")



    return ["/search/result/item/1.txt", "/search/result/item/2.txt", "/search/result/item/3.txt"]


class IOUtilException(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(IOUtilException, msg, *args)

    def __str__(self):
        return self.msg
