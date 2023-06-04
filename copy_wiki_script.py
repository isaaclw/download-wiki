import os
import requests
import tempfile
from bs4 import BeautifulSoup
NAMESPACE_MAP = {
    'main': 0,
    'file': 6,
    'template': 10,
    'categories': 14,
    'talk': 1,
}


def download_all(domain, name, file):
    """
    To download all the details, we need to post
    Download the page's xml and all the related details, and store it at
    the file
    """
    print("downloading %s to %s" % (name, file))
    url = 'http://%s/w/index.php?title=Special:Export&action=submit' % (
            domain)

    response = requests.post(url, {
        'templates': 1,
        'pages': name,
        })
    print(response.content)
    datagen, headers = poster.encode.multipart_encode(params)
    request = urllib.Request(url, datagen, headers)
    result = urllib.urlopen(request)
    if not os.path.exists(os.path.split(file)[0]):
        os.makedirs(os.path.split(file)[0])
    open(file, 'wb').write(result.read())


def download_files(domain, name, file):
    """
    To download all the details, we need to post
    Download the page's xml and all the related details, and store it at
    the file
    """
    print("downloading %s to %s" % (name, file))
    name = urllib.quote(name)
    url = 'http://%s/wiki/File:%s' % (
            domain, name)
    parsed_html = BeautifulSoup(urllib.urlopen(url))
    page_list = [l for l in parsed_html.body.findAll('a')
            if (len(l.findChildren('img')) > 0 or 'Full resolution' in str(l))]

    url = "http://%s%s" % (domain, page_list[0]['href'])
    urllib.urlretrieve(url, file)


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
        return [l['href'].lstrip('/wiki/').encode('utf8')
                for l in parsed_html.body.find('ul',
                    attrs={'class':'mw-allpages-chunk' }
                ).findChildren('a') ]

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
                parsed_html = BeautifulSoup(page.content)
                pagelist = pagelist.union(parse_page_for_title(parsed_html))

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
        fcache.write("%s\n" % page)
    fcache.close()
    return True


def get_list(domain_from, pl_cache, namespace='main'):
    page_list = load_cache(pl_cache)
    if len(page_list) <= 1:
        page_list = list(find_pages(domain_from, namespace))
        write_cache(pl_cache, page_list)
    return page_list


def copy_wiki_pages(domain_from, pl_cache=None, ddir=None,
        namespace='main'):
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
        download_file = os.path.join(ddir, fname)
        if os.path.isfile(download_file):
            continue

        if namespace == 'file':
            download_files(domain_from, page, download_file)
        else:
            download_all(domain_from, page, download_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--from',
            dest='domain_from',
            )
    parser.add_argument('--page-list',
            dest='page_list',
            default='pages.txt'
            )
    parser.add_argument('--xml-dir',
            dest='xdir',
            default=None,
            )
    parser.add_argument('--file-list',
            dest='file_list',
            default='files.txt',
            )
    parser.add_argument('--file-dir',
            dest='fdir',
            default=None,
            )
    parser.add_argument('--template-list',
            dest='template_list',
            default='templates.txt',
            )
    parser.add_argument('--template-dir',
            dest='tedir',
            default=None,
            )
    parser.add_argument('--category-list',
            dest='category_list',
            default='categories.txt',
            )
    parser.add_argument('--category-dir',
            dest='cdir',
            default=None,
            )
    parser.add_argument('--talk-list',
            dest='talk_list',
            default='categories.txt',
            )
    parser.add_argument('--talk-dir',
            dest='tadir',
            default=None,
            )
    args = parser.parse_args()

    if args.domain_from is None:
        parser.error('You need to provide a domain')

    if args.xdir is not None:
        copy_wiki_pages(args.domain_from, pl_cache=args.page_list,
                ddir=args.xdir, namespace='main')
    if args.fdir is not None:
        copy_wiki_pages(args.domain_from, pl_cache=args.file_list,
                ddir=args.fdir, namespace='file')
    if args.tedir is not None:
        copy_wiki_pages(args.domain_from, pl_cache=args.template_list,
                ddir=args.tedir, namespace='template')
    if args.cdir is not None:
        copy_wiki_pages(args.domain_from, pl_cache=args.category_list,
                ddir=args.cdir, namespace='categories')
    if args.tadir is not None:
        copy_wiki_pages(args.domain_from, pl_cache=args.talk_list,
                ddir=args.tadir, namespace='talk')
