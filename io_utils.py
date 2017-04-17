import random
import sqlite3
import os
import time,calendar
import file_parser
from io import StringIO, BytesIO

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'database.sqlt')


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
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        selectStatement = "SELECT file_name from file WHERE file_path = ? AND file_name =  ? AND file_type = 'file';"
        selectData = (path, filename)
        c.execute(selectStatement,selectData)
        fileList = c.fetchall()
        decoded_data = data.decode("utf-8", "ignore")

        if(len(fileList) == 0):

            #insert file
            statement = "INSERT INTO file (file_type, file_name, file_path,file_data, file_size) values (?,?,?,?,?)"
            values = ("file", filename, path ,data,len(data))
            c.execute(statement,values)
            conn.commit()

            #insert keywords
            words = None
            fileExtension = filename.split(".")[-1]
            if fileExtension == "pdf":
                words = file_parser.get_word_counts(file_parser.pdf_to_text(BytesIO(data)))
            elif fileExtension == "txt":
                words = file_parser.get_word_counts(decoded_data)
            file_id_select = "SELECT file_id FROM file WHERE file_path = ? and file_name = ? and file_type = 'file' and file_data = ? and file_size = ?"
            file_id_values = (path, filename, data, len(data))
            c.execute(file_id_select, file_id_values)
            file_id = c.fetchone()[0]
            f = open("./file_data/" + str(file_id), "wb")
            f.write(data)
            c.close()

            if words:
                insert_keywords(words,file_id)


        else:
            raise IOUtilException("File Already Exists")
        conn.close()
    except Exception as e:
        raise IOUtilException(str(e))


def insert_keywords(keywords, file_id):
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        insert_statement = "INSERT INTO keyword (file_id, keyword, count) VALUES (?,?,?)"
        for word in keywords:
            insert_values = (file_id,word[0], int(word[1]))
            c.execute(insert_statement, insert_values)
        conn.commit()
        conn.close()
    except Exception as e:
        raise IOUtilException(str(e))






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
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        selectStatement = "SELECT file_name from file WHERE file_path = ? AND file_name =  ? AND file_type = 'folder';"
        selectData = (path, new_folder_name)
        c.execute(selectStatement,selectData)
        fileList = c.fetchall()
        if(len(fileList) == 0):
            statement = "INSERT INTO file (file_type, file_name, file_path) values (?,?,?)"
            data = ("folder", new_folder_name, path)
            c.execute(statement,data)
            conn.commit()
            conn.close()
        else:
            raise IOUtilException("Folder Already Exists")
    except Exception as e:
        raise IOUtilException(str(e))




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
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        statement = "SELECT * FROM file WHERE file_path LIKE ?"
        data = (path,)
        c.execute(statement,data)
        aList = c.fetchall()
        for file in aList:
            p='%Y-%m-%d %H:%M:%S'
            epoch = calendar.timegm(time.strptime(file[4], p)) * 1000
            fileList.append({"type":file[1],"name":file[2],"date_added":epoch,"size_bytes": file[6] if file[6] != None else -1})
        conn.close()
        return fileList
    except Exception as e:
        raise IOUtilException(str(e))



        #[{"type": "folder", "name": "sample folder", "date_added": 1490401135674, "size_bytes": -1},
            #{"type": "file", "name": "sample file 1.txt", "date_added": 1490401135674, "size_bytes": 10649}]


def get_file_contents_location(path):
    """
    Opens a given file and returns the name of the actual file on disk.

    :param path: the path of the file including the filename and extension
    :return: a string of the true file
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    file_name = path.strip().split("/")[-1]
    file_path =  "/" + ("/".join(path.strip().split("/")[:-1]))+ "/"
    select_values = (file_path,file_name)
    print(select_values)
    select_statement = "SELECT file_id FROM file WHERE file_path = ? AND file_name = ?"
    c.execute(select_statement, select_values)
    file_name = c.fetchone()[0]
    return str(file_name)


def delete_item(path):
    """
    Remove a file or folder from the filesystem. If the path is a folder, should recursively remove all files
    and folders in the path before removing the path.

    :param path: A string of a path. May contain a filename or a folder. 
    :return: None
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        if path[:2] == "//":
            path1 = path[:2]
        else:
            path1 = ("/".join(path.strip().split("/")[:-1]))+ "/"

        if path[-1] == "/":
            folder = True
            file_name = path.strip()[:-1].split("/")[-1]
            path1 = ("/".join(path[:-1].strip().split("/")[:-1]))+ "/"
            if path1 == "//":
                pathDelete = "/"
            else:
                pathDelete = path1
        else:
            file_name = path.strip().split("/")[-1]
            folder = False
        statement = "SELECT file_name, file_type, file_path FROM file WHERE file_path = ?;"
        values = (path1,)
        c.execute(statement,values)
        aList = c.fetchall()
        deleteKeyword = "DELETE FROM keyword WHERE file_id = ?"
        for file in aList:
            if(file[1] == "file" and file[0] == file_name and not folder):
                deleteStatement = "DELETE FROM file WHERE file_name = ? AND file_type = 'file' and file_path = ?;"
                selectIDStatement = "SELECT file_id FROM file WHERE file_name = ? and file_type = 'file' and file_path = ?"
                deleteData = (file[0], path1)
                c.execute(selectIDStatement,deleteData)
                file_id = c.fetchone()[0]
                os.remove("./file_data/" + str(file_id))
                c.execute(deleteKeyword, (file_id,))                 
                c.execute(deleteStatement,deleteData)

            elif (folder and file[0] == file_name):
                deleteStatement = "DELETE FROM file WHERE file_name = ? AND file_type = 'folder';"
                deleteFiles = "DELETE FROM file WHERE file_path LIKE ?"
                select_file_id = "SELECT file_id from file where file_path LIKE ?"

                deleteData = (file[0],)
                deleteFilesData = (pathDelete + file_name + "%",)
                c.execute(select_file_id, deleteFilesData)
                file_ids = c.fetchall()
                for file_id in file_ids:
                    c.execute(deleteKeyword, (file_id[0],))
                c.execute(deleteStatement, deleteData)
                c.execute(deleteFiles, deleteFilesData)
        conn.commit()
        conn.close()

    except Exception as e:
        raise IOUtilException(str(e))

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
    else:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        select_statement = "SELECT file_id FROM keyword WHERE keyword = ? ORDER BY count DESC LIMIT 10"
        c.execute(select_statement, (search_query,))
        file_ids = c.fetchall()
        file_paths = []
        select_file_statement = "SELECT file_path, file_name FROM file WHERE file_id = ?"
        for fid in file_ids:
            c.execute(select_file_statement, (fid[0],))
            paths = c.fetchone()
            full_path = paths[0] + paths[1]
            file_paths.append(full_path)
        return file_paths
        

        conn.close()

    return []


class IOUtilException(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(IOUtilException, msg, *args)

    def __str__(self):
        return self.msg
