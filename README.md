# File indexer and searcher

## Installation

* Download the directory
* Run the install script `sudo python install.py`
* The directory may now be deleted

The database and log path are saved in /var/lib/file_index_search/config.yaml.

# File indexer

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

Run `file_indexer` to start the indexing.

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

# File searcher

Shows all files or directories that fit the name pattern from the database.

It prints:

* file path
* file type
* file size
* last modification date

## Usage

Run `file_search [pattern]` to search.

Optional arguments:

* -h, --help

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print the help message
* --minSize

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;filter by minimum file size (in bytes), inclusive comparison
* --maxSize

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;filter by maximum file size (in bytes), inclusive comparison
* --case

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;enable case sensitive pattern matching

## TODO

* add more search options
  * order by size or modification date
* maybe: users can only see their own entries (uid)
