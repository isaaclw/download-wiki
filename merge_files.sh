#!/bin/bash

(
    echo "";
    cat $@ | grep -Ev "^<\/?mediawiki.*?>";
    echo ""
)  > ~/xml-download.xml
