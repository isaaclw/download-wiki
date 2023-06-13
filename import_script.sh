#!/bin/bash
set -e

php_ini=/home/isaac/.php.ini
user=www-data

application=$1
import_folder=$2

if [ -z "$import_folder" ]; then
    echo "provide [ application ] [ import_folder ]"
    exit 1
fi

cd "$import_folder"
folders=(
    'main'
    'talk'
    'user'
    'user talk'
#    'file'  # this one is imported a different way
    'file talk'
    'mediawiki'
    'mediawiki talk'
    'template'
    'template talk'
    'help'
    'help talk'
    'category'
    'category talk'
)

sudo -v
for folder in ${folders[@]}; do
    ls "$import_folder/$folder/" | while read file; do
        full_filename="$import_folder/$folder/$file"
        echo "importing $full_filename"
        sudo -u $user php -c $php_ini "$application"/maintenance/importDump.php < "$full_filename"
    done
done

sudo -u $user php -c $php_ini "$application"/maintenance/importImages.php "$import_folder/files/"


sudo -u $user php -c $php_ini "$application"/maintenance/rebuildrecentchanges.php
sudo -u $user php -c $php_ini "$application"/maintenance/initSiteStats.php
