#!/usr/bin/env python
# -*- coding: utf-8 -*-
from variant import Variant
from sweepers.sweeper_ma import SweeperMA
from sweepers.sweeper_to import SweeperTO


class SweeperFactory:
    """
    Sweeper can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    RETRY = 50

    def __init__(self, main_url, dry_run, filters, reverse=False, use_proxies=True):
        """Initialize the Collector object
        :param main_url: <str> The URL from which to collect chapters and other info
        :param dry_run: <bool> Will only print and not download
        :return: None
        """
        super().__init__()
        self.main_url = main_url
        self.dry_run = dry_run
        self.name = None
        self.chapters = {}
        self.chapter_imgs = {}
        self.reverse = reverse
        self.use_proxies = use_proxies
        self.filters = filters
        self.scraper = None

    def create_sweeper(self, variant):
        if variant == Variant.TO:
            return SweeperTO(
                main_url=self.main_url,
                dry_run=self.dry_run,
                filters=self.filters,
                reverse=self.reverse,
                use_proxies=self.use_proxies,
            )
        elif variant == Variant.MA:
            return SweeperMA(
                main_url=self.main_url,
                dry_run=self.dry_run,
                filters=self.filters,
                reverse=self.reverse,
                use_proxies=self.use_proxies,
            )
