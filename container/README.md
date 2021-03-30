# Containered file indexer

Scans and saves all directory entries in a linux filesystem into a SQLite DB, except "/proc", "/var", "/run", "/sys", "/dev" and "/boot".

## Database

The database saves:
* Entry path as MD5 hash
* Current time
* Entry name
* Entry file extension
* Entry type
* Entry path
* Entry path as placeholder
* Parent directory path
* Entry size
* Creation date
* Last modification date
* Entry owner
* Key as MD5 of entry path, creation date, last modification date and entry owner

## Usage

The first run, i.e. when the database is empty, will take much longer. If the log shows a "started" entry and no "finished" or error entry the application is still working.

Meant for being used as a docker container:

* Run my dockerhub image:

  * `docker run -v /etc/localtime:/etc/localtime:ro --mount source=files-db,target="/etc/files-index" --mount type=bind,source="/",target=" host",readonly mmdockermmmm/indexer_ubuntu`

* Build it yourself with the Dockerfile:

  * `docker build -t [tag] .` 
  
  * `docker run -v /etc/localtime:/etc/localtime:ro --mount source=files-db,target="/etc/files-index" --mount type=bind,source="/",target=" host",readonly [tag]`

Run `docker inspect files-db` for the database and log location on the container.

To use outside a container: 

* change the LOG_FILENAME value to a path of your choice (~ line 13)
* change the database path for the connection to a path of your choice (~ line 23)
* change the dir_path to a path of your choice ("/") (~ line 290)
* change the prefix to an empty string (~ line 292)

The lines to change are tagged with the comment `#change this for running outside container`.

## Use as a service

Copy the mindex.service and mindex.timer to /etc/systemd/system.

Enable (and start) the service and timer. By default it will run 15 minutes after systemd start and every 12 hours after that.


## TODO

* General optimizations and bug fixes
* Change the try for UnicodeEncodeError so that it doesn't just skip the entry (it currently is a workaround because it threw errors at multiple places)
* Make is_hidden() work for directories like /home/moritz/.mozilla
* Why are all entries counted as symlinks
* Add more exception handling
* Make excluding /... directories optional
* Make exckuding hidden directories optional
* File extension field for directories should be null
* Get input from user to decide which directory to scan (in run command?)
* Check .is_dir() less often
* Why is the output printed only after the scan is run?
* Maybe use os.walk() instead of own function
* Make it work for windows
