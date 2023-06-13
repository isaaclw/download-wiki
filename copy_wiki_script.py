#!/usr/bin/env python3
import os
import requests
import tempfile
from bs4 import BeautifulSoup
NAMESPACE_MAP = {
    'main': 0,
    'talk': 1,
    'user': 2,
    'user talk': 3,
    'file': 6,
    'file talk': 7,
    'mediawiki': 8,
    'mediawiki talk': 9,
    'template': 10,
    'template talk': 11,
    'help': 12,
    'help talk': 13,
    'category': 14,
    'category talk': 15
}


def download_all(domain, name, file):
    """
    To download all the details, we need to post
    Download the page's xml and all the related details, and store it at
    the file
    """
    print("downloading %s to %s" % (name, file))
    url = 'http://%s/index.php?title=Special:Export&action=submit' % (
            domain)

    response = requests.post(url, {
        'templates': 1,
        'pages': name,
        })
    open(file, 'wb').write(response.content)


def download_files(domain, name, file):
    """
    To download all the details, we need to post
    Download the page's xml and all the related details, and store it at
    the file
    """
    url = 'http://%s/wiki/%s' % (
            domain, name)
    print("downloading %s to %s" % (url, file))
    response = requests.get(url)
    parsed_html = BeautifulSoup(response.content, features="html.parser")
    page_list = [l for l in parsed_html.body.find(
            'div', attrs={'id': 'bodyContent'}).findAll('a')
            if (len(l.findChildren('img')) > 0 or 'Original file' in str(l))]

    url = "http://%s%s" % (domain, page_list[0]['href'])
    print('url = %s' % url)
    response = requests.get(url)
    open(file, 'wb').write(response.content)


def find_pages(domain, namespace='main'):
    """
    Scans the 'Special:AllPages' and uses BeuatifulSoup to download a
    list of pages at the specified domain.

    It does this in a two step process since the 'AllPages' page often
    has multiple links listed.
    """

    pagelist = set([])
    url = "http://%s/wiki/Special:AllPages?namespace=%s" % (
                domain, NAMESPACE_MAP[namespace])
    print("downloading %s" % url)
    page = requests.get(url)

    def parse_page_for_title(parsed_html):
        ul_obj = parsed_html.body.find('ul',
                attrs={'class': 'mw-allpages-chunk'})
        if not ul_obj:
            return set([])
        else:
            return set(l['href'].lstrip('/wiki/')
                for l in ul_obj.findChildren('a'))

    def parse_page_for_special_page(parsed_html):
        match_url = '/index.php?title=Special:AllPages'
        return set(a['href'] for a in parsed_html.body.findAll('a')
                   if a.get('href', '').startswith(match_url))

    # parse file
    parsed_html = BeautifulSoup(page.content, features="html.parser")
    # load them into `page_lists`
    special_pages_known = parse_page_for_special_page(parsed_html)

    # If the pages aren't broken down into sub-listings:
    if len(special_pages_known) == 0:
        print("No pagination")
        pagelist = pagelist.union(parse_page_for_title(parsed_html))  # parse the page we just downloaded
    else:  # they're broken down. loop over them
        special_pages_processed = set()
        # While there are pages not yet processed
        while len(special_pages_known - special_pages_processed) > 0:
            process_list = list(special_pages_known - special_pages_processed)
            for url in process_list:
                print("downloading http://%s%s" % (domain, url))
                page = requests.get("http://%s%s" % (domain, url))
                parsed_html = BeautifulSoup(page.content,
                            features="html.parser")
                pagelist |= parse_page_for_title(parsed_html)

                special_pages_processed.add(url)
                special_pages_known |= parse_page_for_special_page(parsed_html)

    return pagelist


def load_cache(pl_cache):
    if pl_cache is None:
        return []
    cache_list = []

    try:
        fcache = open(pl_cache, 'r')
    except IOError:
        open(pl_cache, 'a').close()
    else:
        cache_list = [ line.strip() for line in fcache.readlines() ]
        fcache.close()

    return cache_list


def write_cache(pl_cache, cache_list):
    if pl_cache is None:
        return False

    fcache = open(pl_cache, 'w')
    for page in cache_list:
        fcache.write("%s\n" % str(page))
    fcache.close()
    return True


def get_list(domain_from, pl_cache, namespace='main'):
    page_list = load_cache(pl_cache)
    if len(page_list) <= 1:
        page_list = list(find_pages(domain_from, namespace))
        write_cache(pl_cache, page_list)
    return page_list


def copy_wiki_pages(domain_from, pl_cache, ddir, namespace):
    """
    Specify a domain to download from
        pl_cache: a page list cache file
        ddir: the download directory to safe the file in
    Downloads default from main, but you can specify other pages also.
    """
    page_list = get_list(domain_from, pl_cache, namespace=namespace)

    for page in page_list:
        fname = str(page).replace('/', '_')
        if namespace != 'file':
            fname += '.xml'
        else:
            fname = fname.replace('File:', '')

        download_file = os.path.join(ddir, fname)
        if not os.path.exists(ddir):
            os.makedirs(ddir)

        if os.path.isfile(download_file):
            print("already downloaded: %s, skipping" % download_file)
            continue

        if namespace == 'file':
            download_files(domain_from, page, download_file)
        else:
            download_all(domain_from, page, download_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--from',
            dest='domain_from',
            )

    parser.add_argument('-d', '--download-folder',
            dest='download_folder',
            )
    args = parser.parse_args()

    if args.domain_from is None:
        parser.error('You need to provide a domain')


    for namespace in NAMESPACE_MAP.keys():
        copy_wiki_pages(args.domain_from,
                pl_cache='%s/%s.txt' % (args.download_folder, namespace),
                ddir='%s/%s' % (args.download_folder, namespace),
                namespace=namespace)
