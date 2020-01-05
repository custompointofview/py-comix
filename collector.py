#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import time
import random
import requests as req

from tqdm import tqdm

from concurrent.futures import ThreadPoolExecutor, as_completed

import archive
import sweeper


class Collector:
    """
    Collector can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    TMP_DIR = 'collections'

    def __init__(self, url, dry_run, clean, parallel):
        """Initialize the Collector object
        :param url: <str> The URL from which to collect chapters and other info
        :param dry_run: <bool> Will only print and not download
        :return: None
        """
        super().__init__()
        self.url = url
        self.dry_run = dry_run
        self.clean = clean
        self.parallel = parallel
        self.sweeper = sweeper.Sweeper(main_url=self.url, dry_run=self.dry_run)
        self.packer = archive.Packer()
        self.collection_path = self.TMP_DIR

    def tear_down_collections(self):
        shutil.rmtree(self.TMP_DIR, ignore_errors=True)
        print("=" * 75)

    def tear_down_collection(self):
        for name, url in tqdm(self.sweeper.chapters.items(), desc='# Cleaning'):
            self.tear_down_chapter(name)
        print("=" * 75)

    def tear_down_chapter(self, name):
        shutil.rmtree(os.path.join(self.collection_path, name), ignore_errors=True)

    def collect(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.sweeper.sweep()
        self.collection_path = os.path.join(self.TMP_DIR, self.sweeper.name)
        self.save_collection()
        self.packer.pack_all(self.collection_path)
        if self.clean:
            self.tear_down_collection()

    def save_collection(self):
        print("=" * 75)
        print("# Downloading chapters...")
        # create collection dir
        os.makedirs(self.collection_path, exist_ok=True)
        if not self.parallel:
            for chapter_name, imgs in self.sweeper.chapter_imgs.items():
                self.save_chapter(chapter_name, imgs)
            print("=" * 75)
            return
        print('# Opted for parallel download. CPU count:', os.cpu_count())
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = [executor.submit(self.save_chapter, chapter_name, imgs) for chapter_name, imgs in self.sweeper.chapter_imgs.items()]
            for future in as_completed(futures):
                pass
        print("=" * 75)

    def save_chapter(self, chapter_name, imgs):
        # create dirs for imgs
        col_dir = os.path.join(self.TMP_DIR, self.sweeper.name)
        chapter_dir = os.path.join(col_dir, chapter_name)
        os.makedirs(chapter_dir, exist_ok=True)
        # download images
        for img in tqdm(imgs, desc='# {0}'.format(chapter_name)):
            img_name, img_url = img
            img_path = os.path.join(chapter_dir, img_name)
            # download image
            # sleep randomly so that we mask network behaviour
            time.sleep(random.uniform(0, 0.5))
            r = req.get(img_url, stream=True)
            if r.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
