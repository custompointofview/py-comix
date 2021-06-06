#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import re
import sys

import collector


def validator(args):
    if not args.url:
        return True
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, args.url) is not None


def main(args):
    print(args)
    if not validator(args):
        print("= ERROR: URL is not valid. Please provide a valid URL. Exiting...")
        sys.exit(1)
    if args.json is None:
        parser.print_help()
        return
    with open(args.json) as json_file:
        data = json.load(json_file)
        c = collector.Collector(options=data,
                                dry_run=args.dry,
                                clean=args.clean,
                                parallel=args.parallel,
                                reverse=args.reverse,
                                use_proxies=args.use_proxies)
        # c.collect()
        c.collect_singles()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a comic reader compatible file from a given URL")
    parser.add_argument('-u', '--url',
                        type=str,
                        metavar="url",
                        help="URL to scrape chapters from")
    parser.add_argument('-j', '--json',
                        type=str,
                        metavar="json",
                        help="Path config json")
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
    parser.add_argument('-r', '--reverse',
                        help="reverse execution on chapters",
                        dest="reverse", action="store_true")
    parser.add_argument('-v', '--verbose',
                        help="verbose execution",
                        dest="verbose", action="store_true")
    parser.add_argument('-x', '--no-proxies',
                        help="disable proxies",
                        dest="use_proxies", action="store_false")
    args = parser.parse_args()
    main(args)
