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
from variant import Variant
from sweepers.factory import SweeperFactory


class Collector:
    """
    Collector can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    TMP_COLLECTIONS_DIR = "collections"

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
        self.collection_path = self.TMP_COLLECTIONS_DIR
        self.sweeper = None
        self._init_referer()

    def _init_referer(self):
        self.session = req.session()
        if self.options is not None:
            if (
                "referer" in self.options
                and self.options["referer"] != ""
                and self.options["referer"] is not None
            ):
                print("= Added the referer:", self.options["referer"])
                self.session.headers.update({"referer": self.options["referer"]})
        self.scraper = cloudscraper.create_scraper(sess=self.session)

    def _tear_down_all(self):
        shutil.rmtree(self.TMP_COLLECTIONS_DIR, ignore_errors=True)
        print("=" * 75)

    def _tear_down_collection(self):
        if not os.path.exists(str(self.TMP_COLLECTIONS_DIR)):
            return
        for collection in tqdm(os.listdir(self.TMP_COLLECTIONS_DIR), desc="# Cleaning"):
            coll_path = os.path.join(self.TMP_COLLECTIONS_DIR, collection)
            if not os.path.isdir(coll_path):
                continue
            for chap in os.listdir(coll_path):
                chapter = os.path.join(coll_path, chap)
                if os.path.isdir(chapter) and os.path.isfile(
                    os.path.join(chapter, "1.jpg")
                ):
                    self._tear_down_chapter(chapter)
        print("=" * 75)

    def _tear_down_chapter(self, name):
        abs_path = os.path.abspath(name)
        print("### Removing: ", abs_path)
        shutil.rmtree(abs_path)

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
        rus = self.options["ru"]
        self._collect(rus, Variant.RU)
        tos = self.options["to"]
        self._collect(tos, Variant.TO)
        mas = self.options["manga"]
        self._collect(mas, Variant.MA)
        grs = self.options["graphite"]
        self._collect(grs, Variant.GR)

    def _collect(self, options, variant):
        """INNER COLLECTOR
        :return: None
        """
        print("=" * 75)

        if len(options["urls"]) == 0:
            print("- No URLs in:", variant)
            print("=" * 75)
            return

        print("# Opted for simple collection. CPU count:", os.cpu_count())
        for url in options["urls"]:
            self.sweeper = SweeperFactory(
                main_url=url,
                dry_run=self.dry_run,
                filters=options["filter"],
                reverse=self.reverse,
                use_proxies=self.use_proxies,
            ).create_sweeper(variant)
            self.sweeper.start()
            self.sweeper.sweep()
            self.sweeper.stop()
            self._save_collection()

        print("=" * 75)

    def pack(self):
        self.packer.pack_all(self.collection_path)

    def _pack_all(self):
        self.packer.pack_collections(self.TMP_COLLECTIONS_DIR)

    def clean(self):
        if self.clean_after:
            self._tear_down_collection()

    def close(self):
        if self.scraper is not None:
            self.scraper.close()
        if self.sweeper is not None:
            self.sweeper.close()

    def _save_collection(self):
        """Saves all chapters
        :return: None
        """
        print("=" * 75)
        print("## Saving chapters...")
        # create collection dir
        self.collection_path = self.sweeper.get_name_path(self.TMP_COLLECTIONS_DIR)
        os.makedirs(self.collection_path, exist_ok=True)
        if not self.parallel:
            print("## Opted for simple downloads. CPU count:", os.cpu_count())
            for ch_name, _ in tqdm(
                self.sweeper.chapters.items(), desc="## Saving chapters"
            ):
                self._save_chapter(ch_name, self.sweeper.get_chapter_imgs(ch_name))
        else:
            print("## Opted for parallel downloads. CPU count:", os.cpu_count())
            with ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
                futures = [
                    executor.submit(
                        self._save_chapter,
                        ch_name,
                        self.sweeper.get_chapter_imgs(ch_name),
                    )
                    for ch_name, _ in self.sweeper.chapter_imgs.items()
                ]
                for future in as_completed(futures):
                    pass
        print("=" * 75)

    def _save_chapter(self, chapter_name, imgs):
        """Saves chapter
        :return: None
        """
        # create dirs for imgs
        col_dir = os.path.join(self.TMP_COLLECTIONS_DIR, self.sweeper.name)
        chapter_dir = os.path.join(col_dir, chapter_name)
        os.makedirs(chapter_dir, exist_ok=True)
        # download images
        for img in tqdm(imgs, desc="### {0}".format(chapter_name), ascii=True):
            img_name, img_url = img
            img_path = os.path.join(chapter_dir, img_name)
            if os.path.exists(img_path):
                continue
            self._save_img(img_url=img_url, img_path=img_path)

    def _save_img(self, img_url, img_path):
        # sleep randomly so that we mask network behavior & retry
        ok = False
        for x in range(0, 10):
            for i in range(0, 10):
                time.sleep(random.uniform(0.5, 3))
                # r = req.get(img_url, stream=True)
                r = self.scraper.get(img_url, stream=True, timeout=(60, 60))
                if r.status_code == 200:
                    with open(img_path, "wb") as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    ok = True
                    break
            if ok:
                break
            else:
                print("!!! ERROR downloading IMG: ", img_url)
                self.clean_scraper()
