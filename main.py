#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import re
import sys
import time

import collector
import helpers


def archive(args, options):
    c = collector.Collector(
        options=options,
        dry_run=args.dry,
        clean=args.clean,
        parallel=args.parallel,
        reverse=args.reverse,
        use_proxies=args.use_proxies,
    )
    c._pack_all()
    c.clean()
    c.close()


def collect(args, options):
    c = collector.Collector(
        options=options,
        dry_run=args.dry,
        clean=args.clean,
        parallel=args.parallel,
        reverse=args.reverse,
        use_proxies=args.use_proxies,
    )
    try:
        c.collect()
    except Exception as e:
        print("!!! Exception occured:", e)
        time.sleep(2)
        c.clean()
        c.close()
    c._pack_all()
    c.clean()
    # c.close()


def main(args):
    if not helpers.url_validator(args):
        print("= ERROR: URL is not valid. Please provide a valid URL. Exiting...")
        sys.exit(1)
    # only archive
    if args.archive:
        archive(args, None)
        return
    if args.json is None:
        print("= No configuration given")
        parser.print_help()
        return
    with open(args.json) as json_file:
        options = json.load(json_file)
    # collect
    collect(args, options)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a comic reader compatible file from a given URL"
    )
    parser.add_argument(
        "-a",
        "--archive",
        help="archive the folders of collected images",
        dest="archive",
        action="store_true",
    )
    parser.add_argument(
        "-u", "--url", type=str, metavar="url", help="URL to scrape chapters from"
    )
    parser.add_argument(
        "-j", "--json", type=str, metavar="json", help="Path config json"
    )
    parser.add_argument(
        "-c", "--clean", help="keep only .cbz files", dest="clean", action="store_true"
    )
    parser.add_argument(
        "-p",
        "--parallel",
        help="parallel execution",
        dest="parallel",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        help="only print what you will do",
        dest="dry",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        help="reverse execution on chapters",
        dest="reverse",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="verbose execution", dest="verbose", action="store_true"
    )
    parser.add_argument(
        "-x",
        "--no-proxies",
        help="disable proxies",
        dest="use_proxies",
        action="store_false",
    )
    main(parser.parse_args())
