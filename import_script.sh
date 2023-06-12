#!/bin/bash

php_ini=/home/isaac/.php.ini
user=www-data

application=$1
import_folder=$2

cd "$import_folder"

sudo -v
for folder in templates categories xml talk; do
    ls "$import_folder/$folder/" | while read file; do
        full_filename="$import_folder/$folder/$file"
        echo "importing $full_filename"
        sudo -u $user php -c $php_ini "$application"/maintenance/importDump.php < "$full_filename"
    done
done

sudo -u $user php -c $php_ini "$application"/maintenance/importImages.php "$import_folder/files/"


sudo -u $user php -c $php_ini "$application"/maintenance/rebuildrecentchanges.php
sudo -u $user php -c $php_ini "$application"/maintenance/initSiteStats.php
