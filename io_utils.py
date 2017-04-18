import sqlite3
import os
import calendar
import file_parser
import time
from io import BytesIO

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
        select_statement = "SELECT file_name from file WHERE file_path = ? AND file_name =  ? AND file_type = 'file';"
        select_data = (path, filename)
        c.execute(select_statement, select_data)
        file_list = c.fetchall()
        decoded_data = data.decode("utf-8", "ignore")

        if len(file_list) == 0:
            # insert file
            statement = "INSERT INTO file (file_type, file_name, file_path,file_data, file_size) values (?,?,?,?,?)"
            values = ("file", filename, path, data, len(data))
            c.execute(statement, values)
            conn.commit()

            # insert keywords
            words = None
            file_extension = filename.split(".")[-1]
            if file_extension == "pdf":
                words = file_parser.get_word_counts(file_parser.pdf_to_text(BytesIO(data)))
            elif file_extension == "txt":
                words = file_parser.get_word_counts(decoded_data)
            file_id_select = "SELECT file_id FROM file WHERE file_path = ? and file_name = ? and file_type = 'file' " \
                             "and file_data = ? and file_size = ?"
            file_id_values = (path, filename, data, len(data))
            c.execute(file_id_select, file_id_values)
            file_id = c.fetchone()[0]
            f = open("./file_data/" + str(file_id), "wb")
            f.write(data)
            c.close()

            if words:
                insert_keywords(words, file_id)
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
            insert_values = (file_id, word[0], int(word[1]))
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

        select_statement = "SELECT file_name from file WHERE file_path = ? AND file_name =  ? AND file_type = 'folder';"
        select_data = (path, new_folder_name)
        c.execute(select_statement, select_data)
        file_list = c.fetchall()
        if len(file_list) == 0:
            statement = "INSERT INTO file (file_type, file_name, file_path) values (?,?,?)"
            data = ("folder", new_folder_name, path)
            c.execute(statement, data)
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
    file_list = []
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        statement = "SELECT * FROM file WHERE file_path LIKE ?"
        data = (path,)
        c.execute(statement, data)
        a_list = c.fetchall()
        for file in a_list:
            p = '%Y-%m-%d %H:%M:%S'
            epoch = calendar.timegm(time.strptime(file[4], p)) * 1000
            file_list.append({"type": file[1], "name": file[2], "date_added": epoch,
                              "size_bytes": file[6] if file[6] is not None else -1})
        conn.close()
        return file_list
    except Exception as e:
        raise IOUtilException(str(e))


def get_file_contents_location(path):
    """
    Opens a given file and returns the name of the actual file on disk.

    :param path: the path of the file including the filename and extension
    :return: a string of the true file
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    file_name = path.strip().split("/")[-1]
    file_path = "/" + ("/".join(path.strip().split("/")[:-1])) + "/"
    select_values = (file_path, file_name)
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
            path1 = ("/".join(path.strip().split("/")[:-1])) + "/"

        if path[-1] == "/":
            folder = True
            file_name = path.strip()[:-1].split("/")[-1]
            path1 = ("/".join(path[:-1].strip().split("/")[:-1])) + "/"
            if path1 == "//":
                path_delete = "/"
            else:
                path_delete = path1
        else:
            file_name = path.strip().split("/")[-1]
            path_delete = ""
            folder = False
        statement = "SELECT file_name, file_type, file_path FROM file WHERE file_path = ?;"
        values = (path1,)
        c.execute(statement, values)
        a_list = c.fetchall()
        delete_keyword = "DELETE FROM keyword WHERE file_id = ?"
        for file in a_list:
            if file[1] == "file" and file[0] == file_name and not folder:
                delete_statement = "DELETE FROM file WHERE file_name = ? AND file_type = 'file' and file_path = ?;"
                select_id_statement = "SELECT file_id FROM file WHERE file_name = ? and file_type = 'file' " \
                                      "and file_path = ?"
                delete_data = (file[0], path1)
                c.execute(select_id_statement, delete_data)
                file_id = c.fetchone()[0]
                os.remove("./file_data/" + str(file_id))
                c.execute(delete_keyword, (file_id,))
                c.execute(delete_statement, delete_data)
            elif folder and file[0] == file_name:
                delete_statement = "DELETE FROM file WHERE file_name = ? AND file_type = 'folder';"
                delete_files = "DELETE FROM file WHERE file_path LIKE ?"
                select_file_id = "SELECT file_id from file where file_path LIKE ?"

                delete_data = (file[0],)
                delete_files_data = (path_delete + file_name + "%",)
                c.execute(select_file_id, delete_files_data)
                file_ids = c.fetchall()
                for file_id in file_ids:
                    c.execute(delete_keyword, (file_id[0],))
                c.execute(delete_statement, delete_data)
                c.execute(delete_files, delete_files_data)
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
    search_queries = search_query.lower().split()
    start = time.time()

    if len(search_query) < 4:
        raise IOUtilException("query too short")
    else:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        question_marks = ",".join(["?"] * len(search_queries))
        select_statement = "SELECT DISTINCT file_id FROM keyword WHERE keyword IN ({}) ORDER BY count DESC LIMIT 10"\
            .format(question_marks)
        c.execute(select_statement, search_queries)
        file_ids = c.fetchall()
        file_paths = []
        select_file_statement = "SELECT file_path, file_name FROM file WHERE file_id = ?"
        for fid in file_ids:
            c.execute(select_file_statement, (fid[0],))
            paths = c.fetchone()
            full_path = paths[0] + paths[1]
            file_paths.append(full_path)
        conn.close()

        if not len(file_paths):
            raise IOUtilException("no results")

        results = {"files": file_paths, "time": round(time.time() - start, 5)}
        return results


class IOUtilException(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(IOUtilException, msg, *args)

    def __str__(self):
        return self.msg
