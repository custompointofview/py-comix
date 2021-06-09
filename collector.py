#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import time
import random
import requests as req

from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor, as_completed
# Commenting out cfsrape as it doesn't work anymore. Trying different approach with - cloudscraper
# import cfscrape
import cloudscraper

from packer import Packer
from sweeper import SweeperFactory
from variant import Variant


class Collector:
    """
    Collector can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    TMP_DIR = 'collections'

    def __init__(self, options, dry_run, clean, parallel, reverse, use_proxies=True):
        """Initialize the Collector object
        :param url: <str> The URL from which to collect chapters and other info
        :param dry_run: <bool> Will only print and not download
        :return: None
        """
        super().__init__()
        self.dry_run = dry_run
        self.clean_after = clean
        self.parallel = parallel
        self.options = options
        self.reverse = reverse
        self.use_proxies = use_proxies
        self.packer = Packer()
        self.collection_path = self.TMP_DIR

        self.sweeper = None
        self.session = req.session()
        if 'referer' in options and options['referer'] != '' and options['referer'] is not None:
            print("= Added the referer:", options['referer'])
            self.session.headers.update({'referer': options['referer']})
        self.scraper = cloudscraper.create_scraper(sess=self.session)

    def tear_down_collections(self):
        shutil.rmtree(self.TMP_DIR, ignore_errors=True)
        print("=" * 75)

    def tear_down_collection(self):
        for name, url in tqdm(self.sweeper.chapters.items(), desc='# Cleaning'):
            self.tear_down_chapter(name)
        print("=" * 75)

    def tear_down_chapter(self, name):
        shutil.rmtree(os.path.join(self.collection_path, name),
                      ignore_errors=True)

    def clean_scraper(self):
        print("### Something went wrong. Cleaning scraper...")
        self.session.close()
        self.scraper.close()
        self.session = req.session()
        self.scraper = cloudscraper.create_scraper(sess=self.session)

    def collect(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        rus = self.options['ru']
        self._collect(rus, Variant.RU)
        tos = self.options['to']
        self._collect(tos, Variant.TO)
        mas = self.options['manga']
        self._collect(mas, Variant.MA)
        grs = self.options['graphite']
        self._collect(grs, Variant.GR)

    def _collect(self, options, variant):
        """INNER COLLECTOR
        :return: None
        """
        if len(options['urls']) == 0:
            print('## No URLs in:', variant)
            return
        for url in options['urls']:
            self.sweeper = SweeperFactory(main_url=url,
                                          dry_run=self.dry_run,
                                          filters=options['filter'],
                                          reverse=self.reverse,
                                          use_proxies=self.use_proxies).create_sweeper(variant)
            self.sweeper.announce()
            self.sweeper.sweep_collection()
            self.collection_path = self.sweeper.get_name_path(self.TMP_DIR)
            for ch_name, ch_url in tqdm(self.sweeper.chapters.items(), desc='## Collecting'):
                print("### Collecting: ", ch_name)
                self.sweeper.try_sweep_chapter(ch_url, ch_name)
                self.save_chapter(ch_name, self.sweeper.get_chapter_imgs(ch_name))

    def pack(self):
        self.packer.pack_all(self.collection_path)

    def clean(self):
        if self.clean_after:
            self.tear_down_collection()

    def save_collection(self):
        """Saves all chapters
        :return: None
        """
        print("=" * 75)
        print("## Downloading chapters...")
        # create collection dir
        os.makedirs(self.collection_path, exist_ok=True)
        if not self.parallel:
            for chapter_name, imgs in self.sweeper.chapter_imgs.items():
                self.save_chapter(chapter_name, imgs)
            print("=" * 75)
            return
        print('## Opted for parallel download. CPU count:', os.cpu_count())
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = [executor.submit(self.save_chapter, chapter_name, imgs) for chapter_name, imgs in
                       self.sweeper.chapter_imgs.items()]
            for future in as_completed(futures):
                pass
        print("=" * 75)

    def save_chapter(self, chapter_name, imgs):
        """Saves chapter
        :return: None
        """
        # create dirs for imgs
        col_dir = os.path.join(self.TMP_DIR, self.sweeper.name)
        chapter_dir = os.path.join(col_dir, chapter_name)
        os.makedirs(chapter_dir, exist_ok=True)
        # download images
        for img in tqdm(imgs, desc='### {0}'.format(chapter_name), ascii=True):
            img_name, img_url = img
            img_path = os.path.join(chapter_dir, img_name)
            if os.path.exists(img_path):
                continue
            # sleep randomly so that we mask network behaviour & retry
            ok = False
            for x in range(0, 10):
                for i in range(0, 10):
                    time.sleep(random.uniform(0.5, 3))
                    # r = req.get(img_url, stream=True)
                    r = self.scraper.get(img_url, stream=True, timeout=(60, 60))
                    if r.status_code == 200:
                        with open(img_path, 'wb') as f:
                            for chunk in r.iter_content(1024):
                                f.write(chunk)
                        ok = True
                        break
                if ok:
                    break
                else:
                    print("!!! ERROR downloading IMG: ", img_url)
                    self.clean_scraper()

    def close(self):
        self.scraper.close()
        self.sweeper.close()
