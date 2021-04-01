import yaml, os, shutil, sys, subprocess

def get_choice():    
    while True:
        choice = input("Choose Installation:\n   1 Native installation\n   2 Installation as container ")
        #depending on the shell the input might be either int or string
        if choice == 1 or choice == "1":
            print("Installing natively...")
            return 1
        if choice == 2 or choice == "2":
            print("Installing as container...")
            return 2
        
def main():
    db_path = ""
    log_path = ""
    prefix = ""
    entrypoint = "" #entrypoint directory for the indexing
    while not os.path.exists(entrypoint):
        entrypoint = input("Please enter the entry point for the indexer: ")
    installation = "native" #this value is never used and is just to verify from the config which installation was chosen
    config_dir = "/var/lib/file_index_search/"
    scripts_dir = "/usr/local/bin/"
    indexer = "file_indexer.py"
    searcher = "file_search.py"
    
    if get_choice() == 1:        
        #move executable file_indexer
        os.rename(indexer, indexer[:-3]) #remove file extension
        indexer = indexer[:-3]        
        os.chmod(indexer, 0o744)

        #if the script is run without enough permission, rerunning will break on the next run because filenames already changed
        try:
            #move to directory included in PATH
            shutil.move(indexer, scripts_dir) 
        except shutil.Error:
            os.remove(os.path.join(scripts_dir, indexer))
            shutil.move(indexer, scripts_dir)
        except Exception as e:
            print(e)
            sys.exit("Couldn't move the python files to the destination directory")

        #location where database and logs are saved
        db_dir = ""
        while not os.path.exists(db_dir):
            db_dir = input("Please enter the directory path for the database and log: ")

        db_path = os.path.join(db_dir, "files.db")
        log_path = os.path.join(db_dir, "status.log")
    else:
        #just create logs for container installation
        #when it is run as a container, db_path and log_path aren't needed for the indexer itself
        db_path = "/var/lib/docker/volumes/files-db/_data/files.db"
        log_path = "/var/lib/docker/volumes/files-db/_data/status.log"
        entrypoint = "/host" + entrypoint
        prefix = "/host"
        installation = "container"
        subprocess.call(["docker", "build", "-t", "indexer", "."])
        #print("Run 'docker build -t name .' to build the image.")
        print("Run 'docker run -v /etc/localtime:/etc/localtime:ro --mount source=files-db,target=\"/etc/files-index\" --mount type=bind,source=\"/\",target=\"/host\",readonly indexer' to use the indexer.")

    #move executable file_search
    #remove file extension
    os.rename(searcher, searcher[:-3])
    searcher = searcher[:-3]
    os.chmod(searcher, 0o744)
    try:   
        #move to directory included in PATH
        shutil.move(searcher, scripts_dir)
    except shutil.Error:
        os.remove(os.path.join(scripts_dir, searcher))
        shutil.move(searcher, scripts_dir)
    except Exception as e:
        print(e)
        sys.exit("Couldn't move the python files to the destination directory")

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