#!/usr/bin/env python3
import argparse, sqlite3, sys, yaml

def get_path(key):
    with open("/var/lib/file_index_search/config.yaml") as config:
        try:
            dictionary = yaml.safe_load(config)
        except yaml.YAMLError as e:
            print("Error: Using default path", e)
            dictionary = { "db_path": "/var/lib/file_index_search/files.db", "log_path": "/var/lib/file_index_search/status.log" }
    return dictionary[key]

try:
    connection = sqlite3.connect(get_path("db_path"))
    #connection = sqlite3.connect('/var/lib/docker/volumes/files-db/_data/files.db')
    c = connection.cursor()
except Exception as e:
    print("Exception:", e)
    sys.exit("Invalid database path")

def print_entries(pattern, minSize, maxSize, case):
    if case:
        c.execute('PRAGMA case_sensitive_like = on')

    c.execute('''SELECT FileFullPath, FileType, FileSize, FileLastModificationDate
                FROM Files
                WHERE FileFullPath LIKE ? AND FileSize >= ? AND FileSize <= ?''', ('%' + pattern + '%', minSize, maxSize))

    for result in c:
        print(f'{result[0]} | {result[1]} | {result[2] / 1000:.2f} kB | last modified at {result[3]}')

def main():  
    parser = argparse.ArgumentParser(description='Search for files and directories in the database')
    parser.add_argument('pattern', help='pattern of the file or directory to search')
    parser.add_argument('--minSize', help='filter by minimum file size (in bytes)', type=int, default=0)
    parser.add_argument('--maxSize', help='filter by maximum file size (in bytes)', type=int, default=9000000000000000000)
    parser.add_argument('--case', help='enable case sensitive pattern matching', action='store_true')
    args = parser.parse_args()
    print_entries(args.pattern, args.minSize, args.maxSize, args.case)

    c.close()
    connection.close

if __name__ == "__main__":
    main()