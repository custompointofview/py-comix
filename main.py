#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import re
import sys

import collector
import archive


def threaded_factory(url, dry):
    pass


def single_factory(url, dry):
    c = collector.Collector(main_url=url, dry_run=dry)
    c.collect()
    p = archive.Packer('archives')
    p.pack_all()


def main(args):
    if args.parallel:
        threaded_factory(url=args.url, dry=args.dry)
        return
    single_factory(url=args.url, dry=args.dry)


def validator(args):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, args.url) is not None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a comic reader compatible file from a given URL")
    parser.add_argument('url',
                        type=str,
                        metavar="url",
                        help="URL to scrape chapters from")
    parser.add_argument('-c', '--clean',
                        help="keep only .cbz files",
                        dest='clean', action="store_true")
    parser.add_argument('-p', '--parallel',
                        help="parallel execution",
                        dest='parallel', action="store_true")
    parser.add_argument('-d', '--dry-run',
                        help="only print what you will do",
                        dest="dry", action="store_true"
                        )
    parser.add_argument('-v', '--verbose',
                        help="verbose execution",
                        dest="verbose", action="store_true")
    a = parser.parse_args()
    print(a)
    if not validator(a):
        print("= ERROR: URL is not valid. Please provide a valid URL. Exiting...")
        sys.exit(1)
    main(a)
