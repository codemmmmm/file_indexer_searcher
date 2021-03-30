import yaml, os, shutil, sys, subprocess

def get_choice():    
    while True:
        choice = input("Choose Installation:\n   1 Native installation\n    2 Installation as container")
        if choice == "1":
            print("Installing natively...")
            return 1
        if choice == "2":
            print("Installing as container...")
            return 2
        
def main():
    db_path = ""
    log_path = ""
    prefix = ""
    entrypoint = ""
    while not os.path.exists(entrypoint):
        entrypoint = input("Please enter the entry point for the indexer: ")
    installation = "native" #this value is never used
    config_dir = "/var/lib/file_index_search/"
    
    if get_choice() == 1:
        scripts_dir = "/usr/local/bin/"
        indexer = "file_indexer.py"
        searcher = "file_search.py"

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
        
        #if the script is run without enough permission, rerunning will break on the next run because filenames already changed
        try:   
            shutil.move(searcher, scripts_dir)
        except shutil.Error:
            os.remove(os.path.join(scripts_dir, searcher))
            shutil.move(searcher, scripts_dir)
        except Exception as e:
            print(e)
            sys.exit("Couldn't move the python files to the destination directory")

        db_dir = ""
        while not os.path.exists(db_dir):
            db_dir = input("Please enter the directory path for the database and log: ")

        db_path = os.path.join(db_dir, "files.db")
        log_path = os.path.join(db_dir, "status.log")
        data = { "db_path": db_path, "log_path": log_path, "entrypoint": entrypoint }
    else:
        db_path = "/var/lib/docker/volumes/files-db/_data/files.db"
        log_path = "/var/lib/docker/volumes/files-db/_data/status.log"
        entrypoint = "/host" + entrypoint
        prefix = "/host"
        installation = "container"
        print("Run 'docker build -t [name] .' to build the image")

    data = dict()
    data["installation"] = installation
    data["db_path"] = db_path
    data["log_path"] = log_path
    data["entrypoint"] = entrypoint
    data["prefix"] = prefix
    #data = { "db_path": db_path, "log_path": log_path, "entrypoint": entrypoint }

    if not os.path.isdir(config_dir):
            os.mkdir(config_dir)

    with open(config_dir + "config.yaml", "w") as config:
        yaml.dump(data, config)

    print("Finished")

if __name__ == "__main__":
    main()