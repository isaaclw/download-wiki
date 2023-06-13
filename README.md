download-wiki
=============

This is a very simple download wiki script that parses the export page on an external wiki so that the files can be downloaded and imported someplace else.
Because it is looking for specific links, you may need to make sure that the links match your own.

# It supports downloading:
- Categories
- Templates
- Pages
- Files

# install
    mkvirtualenv download-wiki
    pip3 install beautifulsoup4 requests

# Running export:
    ../copy_wiki_script.py -f <domain> -d ./dl
    cp import_script.sh dl/
    rsync -av dl remote_server:wiki_dump

# Running the import
Now on the remote server

    cd wiki_dump
    ./import_script.sh <application_folder> ./wiki_dump/

In my case, the application folder was in /var/www/ where I had installed the wiki.


Add you'll see output like this:

    importing xml/<file>.xml
    100 (6.82 pages/sec 48.08 revs/sec)
    100 (6.82 pages/sec 48.14 revs/sec)
    100 (6.82 pages/sec 48.20 revs/sec)
    100 (6.82 pages/sec 48.33 revs/sec)
    Done!
    You might want to run rebuildrecentchanges.php to regenerate RecentChanges,
    and initSiteStats.php to update page and revision counts

