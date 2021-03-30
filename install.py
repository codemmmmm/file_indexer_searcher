import yaml, os, shutil, sys, subprocess

def main():
    #scripts_dir = "/usr/local/bin/file_index_search"
    scripts_dir = "/usr/local/bin/"
    indexer = "file_indexer.py"
    searcher = "file_search.py"
    config_dir = "/var/lib/file_index_search"

    os.rename(indexer, indexer[:-3])
    os.rename(searcher, searcher[:-3])
    indexer = indexer[:-3]
    searcher = searcher[:-3]
    os.chmod(indexer, 0o744)     
    os.chmod(searcher, 0o744)

    try:
        shutil.move(indexer, scripts_dir) 
    except shutil.Error:
        os.remove(os.path.join(scripts_dir, indexer))
        shutil.move(indexer, scripts_dir)
    except Exception as e:
        print(e)
        sys.exit("Couldn't move the python files to the destination directory")
    
    #if the script is run without enough permission, rerunning will break because filenames already changed
    try:   
        shutil.move(searcher, scripts_dir)
    except shutil.Error:
        os.remove(os.path.join(scripts_dir, searcher))
        shutil.move(searcher, scripts_dir)
    except Exception as e:
        print(e)
        sys.exit("Couldn't move the python files to the destination directory")

    #should add option to use a default path
    db_dir = ""
    while not os.path.exists(db_dir):
        db_dir = input("Please enter the directory path for the database and log: ")

    entrypoint = ""
    while not os.path.exists(entrypoint):
        entrypoint = input("Please enter the entry point for the indexer: ")

    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    db_path = os.path.join(db_dir, "files.db")
    log_path = os.path.join(db_dir, "status.log")
    data = { "db_path": db_path, "log_path": log_path, "entrypoint": entrypoint }

    with open(config_dir + "/config.yaml", "w") as config:
        yaml.dump(data, config)

if __name__ == "__main__":
    main()