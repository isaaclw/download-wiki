download-wiki
=============

This is a very simple download wiki script that parses the export page on an external wiki so that the files can be downloaded and imported someplace else.
Because it is looking for specific links, you may need to make sure that the links match your own.

# It supports downloading:
- Categories
- Templates
- Pages
- Files

For an example on use cases:
http://tech.isaaclw.com/2014/09/transwiki-copying.html

# install
    mkvirtualenv download-wiki
    pip3 install beautifulsoup4 requests
