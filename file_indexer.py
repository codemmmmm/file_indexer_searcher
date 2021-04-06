#!/usr/bin/env python3
"""Scans and saves all directory entries in a linux filesystem into a SQLite DB, 
except "/proc", "/var", "/run", "/sys", "/dev" and "/boot".
Configuration data is saved in "/var/lib/file_index_search/config.yaml".
"""

import os, stat, sqlite3, datetime, hashlib, time, logging, collections, yaml, argparse

from logging.handlers import RotatingFileHandler

parser = argparse.ArgumentParser(description='Scan and save all directory entries into a SQLite DB')
parser.add_argument('--container', help='this argument is passed when it is run as container', action='store_true')
args = parser.parse_args()

def get_config_value(key):
    if args.container:
        conf_path = "/host" + "/var/lib/file_index_search/config.yaml"
    else:
        conf_path = "/var/lib/file_index_search/config.yaml"
    with open(conf_path) as config:
        dictionary = {}
        try:
            dictionary = yaml.safe_load(config)
        except yaml.YAMLError as e:
            #change this block
            print("Error: Using default path /var/lib/file_index_search/", e)
            dictionary["db_path"] = "/var/lib/file_index_search/files.db"
            dictionary["log_path"] = "/var/lib/file_index_search/status.log"
    return dictionary[key]

#have to create directory if not exists?
if args.container:
    LOG_FILENAME = "/etc/files-index/status.log"
else:
    LOG_FILENAME = get_config_value("log_path") #change this for running outside container
logger = logging.getLogger('status_logger')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=20000, backupCount=1)
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s", datefmt="%m/%d/%Y %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Started")
try:
    if args.container:
        connection = sqlite3.connect("/etc/files-index/files.db")
    else:
        connection = sqlite3.connect(get_config_value("db_path")) #change this for running outside container
    c = connection.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Files
                (
                MD5_FilePath TEXT,
                CurrentTime TEXT,
                FileName TEXT,
                FileExtension TEXT,
                FileType TEXT,
                FileFullPath TEXT UNIQUE,
                FileFullPathPlaceholder TEXT,
                DirectoryPath TEXT,
                FileSize INTEGER,
                FileCreationDate TEXT,
                FileLastModificationDate TEXT,
                FileOwner TEXT,
                Key TEXT PRIMARY KEY)''')
    connection.commit()
except Exception as e:
    #print("Exception:", e)
    logger.exception("Setting up database")

def get_dir_path():
    """get directory path to index from the user

    :return: The directory path to be scanned
    :rtype: string
    """
    user_input = ""
    while not os.path.isdir(user_input):
        user_input = input("Please enter a valid directory path: ")
    return user_input

def list_files(dir_path, prefix):
    """recursively scans and adds or updates all directory entries

    :param dir_path: directory path
    :type dir_path: string
    :param prefix: path prefix for when it is run as a container with mounted file system
    :type prefix: string
    """
    try:  
        with os.scandir(dir_path) as entries:        
            for entry in entries:
                if entry.is_dir(follow_symlinks=False): 
                    if entry.name.startswith("."):
                        continue               
                    list_files(entry.path, prefix)
                update_entry(entry, dir_path, prefix)
    except Exception as e:
        #print("Exception:", e)
        logger.exception("scanning entries")

def update_entry(f, dir_path, prefix):
    """adds new entry to database or updates the entry if the file has changed:
        file path hashed, current time, file name, file extension, file type,
        file path, file path (placeholder), directory path, file size, 
        file creation date, last modification date, file owner, key

    :param f: directory entry: file or directory (or link)
    :type f: DirEntry
    :param dir_path: directory path
    :type dir_path: string
    :param prefix: path prefix for when it is run as a container with mounted file system
    :type prefix: string
    """
    prefix_length = len(prefix)
    #truncate the path prefix from the mounted directory in the container
    trunc_path = f.path[prefix_length:]
    current_time = get_current_time()
    file_name = f.name
    file_extension = None
    if not f.is_dir():        
        file_extension = os.path.splitext(f.path)[1]
    file_type = get_file_type(f)
    file_full_path = trunc_path 
    file_full_path_placeholder = trunc_path
    directory_path = dir_path[prefix_length:]
    try:
        md5_file_path = md5_path(trunc_path)
    except UnicodeEncodeError as e:
        #print("Exception:", e)
        logger.exception("MD5 Encode Error")
        return 
        #md5_file_path = "UnicodeEncodeError"
        #file_type = "exception"
    try:
        fstat = f.stat(follow_symlinks=False) #throws exception for symbolic links       
    except Exception as e:
        #create own empty f.stat() object when f.stat() doesn't work for an entry
        fstat = collections.namedtuple("fstat", ["st_size", "st_ctime", "st_mtime", "st_uid"])
        fstat.st_size = 0
        fstat.st_ctime = 0
        fstat.st_mtime = 0        
        fstat.st_uid = 0
        file_type = "exception"
        #print("Exception:", e)
        logger.exception("Getting meta data")  
    file_size = fstat.st_size 
    #time of most recent metadata change on Unix or the time of creation on Windows
    file_creation_date = datetime.datetime.fromtimestamp(fstat.st_ctime).strftime("%Y-%m-%d %H:%M:%S") 
    file_last_mod_date = datetime.datetime.fromtimestamp(fstat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    file_owner = fstat.st_uid
    try:
        key = md5_file(trunc_path, file_creation_date, file_last_mod_date, file_owner)
    except UnicodeEncodeError as e:
        key = "UnicodeEncodeError"
        file_type = "exception"
        #print("Exception:", e)
        logger.exception("MD5 Encode Error")
    values = (md5_file_path, current_time, file_name, file_extension,
                file_type, file_full_path, file_full_path_placeholder,
                directory_path, file_size, file_creation_date,
                file_last_mod_date, file_owner, key)

    c.execute("SELECT FileFullPath, Key FROM Files WHERE FileFullPath=?", (trunc_path,))
    entry = c.fetchone()

    #if a file of that path doesn't exist
    if entry is None: 
        add_entry(values)
        #print("added new entry " + f.path)
    else:
        #if file at the path is different (different key) than in DB
        if entry[1] != md5_file(trunc_path, file_creation_date, file_last_mod_date, file_owner):
            c.execute("DELETE FROM Files WHERE FileFullPath=?", (trunc_path,))
            add_entry(values)
            #print("updated entry " + trunc_path)
        #else:
        #    print("didn't change entry " + f.path)   
    
    connection.commit()    

def get_current_time():
    """returns current time

    :return: current time formatted yy-mm-dd hh:mm:ss
    :rtype: string
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_file_type(f):
    """returns file type: "directory", "file" or "symlink" and if it is hidden

    :param f: directory entry: file or directory (or link)
    :type f: DirEntry
    :return: file type
    :rtype: string
    """
    type = ""
    if is_hidden(f.path):
        type = "hidden "
    if f.is_dir():
        type += "dir"
    elif f.is_file():
        type += "file"
    if f.is_symlink:
        type += " symlink"
    return type

#https://stackoverflow.com/questions/284115/cross-platform-hidden-file-detection
#https://stackoverflow.com/questions/20794/find-broken-symlinks-with-python
def is_hidden(filepath):
    """returns true if it is a hidden .file

    :param filepath: file path
    :type filepath: string
    :return: True if it is hidden, else False
    :rtype: bool
    """
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith(".") #or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    """returns true if file has the os stat hidden attribute

    :param filepath: file path
    :type filepath: string
    :return: True if it has the hidden attribute, else False
    :rtype: bool
    """
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

def md5_path(filepath):
    """returns MD5 hash of the file path

    :param path: file path
    :type path: string
    :return: MD5 hash of the file path
    :rtype: string
    """
    return hashlib.md5(filepath.encode()).hexdigest()

def md5_file(path, file_creation_date, file_last_mod_date, file_owner):
    """returns MD5 hash of the file path, creation date, last modification date
    and file owner, serving as key in the database

    :param path: file path
    :type path: string
    :param file_creation_date: file creation date
    :type file_creation_date: string
    :param file_last_mod_date: file last modification date
    :type file_last_mod_date: string
    :param file_owner: file owner id
    :type file_owner: integer
    :return: returns MD5 hash of the arguments as key
    :rtype: string
    """
    hash = hashlib.md5()
    #hashing file content takes too long
    #if f.is_file():
    #    with open(f.path, "rb") as content:
    #        for chunk in iter(lambda: content.read(4096), b""):
    #            hash.update(chunk)
    #hash.update(f.path.encode())
    hash.update(path.encode())
    hash.update(file_creation_date.encode())
    hash.update(file_last_mod_date.encode())
    hash.update(file_owner.to_bytes(8, "big"))
    return hash.hexdigest()

def add_entry(values):
    """SQLite query to insert an entry

    :param values: values for the database entry
    :type values: tuple
    """
    c.execute('''INSERT INTO Files (MD5_FilePath, CurrentTime, FileName,
                FileExtension, FileType, FileFullPath, FileFullPathPlaceholder,
                DirectoryPath, FileSize, FileCreationDate, FileLastModificationDate,
                FileOwner, Key) 
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (values))   

def remove_old_entries(prefix): 
    """removes all old entries from the database

    :param prefix: path prefix for when it is run as a container with mounted file system
    :type prefix: string
    """
    c.execute("SELECT FileFullPath FROM Files")
    entries = c.fetchall()

    c.executemany("DELETE FROM Files WHERE FileFullPath=?", old_entries_generator(entries, prefix))
    connection.commit()

def old_entries_generator(entries, prefix):
    """generator returning all old database entries

    :param entries: tuple of all file paths that exist in the database
    :type entries: tuple
    :param prefix: path prefix for when it is run as a container with mounted file system
    :type prefix: string
    :yield: all database entries that don't exist in the filesystem anymore
    :rtype: tuple
    """
    for entry in entries:    
        path = entry[0] #entry[0] because query returns tuple
        if not os.path.lexists(prefix + path):
            #print("Removed old entry " + path)
            yield (path,)       

def main(): 
    #dir_path = get_dir_path()
    try:   
        dir_path = get_config_value("entrypoint")
        #prefix is the parent directory of the mounted filesystem in the container
        prefix = "/host"
        #print("Started updating DB")
        with os.scandir(dir_path) as entries:        
            for entry in entries:
                if entry.path in (prefix + "/proc", prefix + "/var", prefix + "/run", prefix + "/sys", prefix + "/dev", prefix + "/boot"):
                    continue
                else:
                    list_files(entry.path, prefix)
        #print("Checking for old entries to remove")
        remove_old_entries(prefix)      
        #print("Finished updating DB")
        c.close()
        connection.close()
    except Exception as e:
        #print("Exception:", e)
        logger.exception("Indexing error")
    logger.info("Finished")

if __name__ == "__main__":
    main()