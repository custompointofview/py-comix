#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import shutil
import time
import random

import requests as req

from tqdm import tqdm
from bs4 import BeautifulSoup as bsoup


class Collector:
    """
    Collector can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    TMP_DIR = 'collections'

    def __init__(self, main_url, dry_run):
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
        # create temp dir where to download files
        if not self.dry_run:
            try:
                os.mkdir(self.TMP_DIR)
            except FileExistsError:
                pass

    def tear_down_collection(self):
        shutil.rmtree(self.TMP_DIR, ignore_errors=True)

    def tear_down_chapters(self):
        for name, url in self.chapters.items():
            self.tear_down_chapter(name)

    def tear_down_chapter(self, name):
        shutil.rmtree(os.path.join(self.TMP_DIR, name), ignore_errors=True)

    def collect(self):
        """Collect all chapters and images from chapters
        :return: None
        """

        # collect chapter urls
        self.collect_collection()
        # visit urls and collect images
        for name, url in self.chapters.items():
            chapter_dir = os.path.join(self.TMP_DIR, name)
            if not self.dry_run:
                try:
                    os.mkdir(chapter_dir)
                except FileExistsError:
                    pass
            self.collect_chapter(url, chapter_dir, name)

    def collect_collection(self) -> None:
        print("=" * 75)

        response = req.get(self.main_url)
        html_soup = bsoup(response.text, 'html.parser')

        print("## Finding collection name ...")
        name = html_soup.find('h2', class_='listmanga-header')
        self.name = str(name.contents[0]).strip()
        print('# Name:', self.name)

        print("## Finding chapters ...")
        chapters = html_soup.find('ul', class_='chapters')
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = chapter.a['href']
                chapter_name = chapter.a.contents[0]
                if chapter_name not in self.chapters:
                    print("# Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        print("=" * 75)

    def collect_chapter(self, url, save_path, chapter_name) -> None:
        # sleep because we thread this
        time.sleep(2)
        # get contents from html
        respose = req.get(url)
        html_soup = bsoup(respose.text, 'html.parser')
        img_tags = html_soup.find('div', id='all')
        img_list = list(img_tags.findChildren())
        for img_tag in tqdm(img_list, desc=chapter_name):
            # sleep randomly so that we mask network behaviour
            time.sleep(random.uniform(0, 0.5))
            # get img url & strip
            if self.dry_run:
                # print("# Image: ", img_url)
                continue
            # download image
            img_url = str(img_tag['data-src']).strip()
            r = req.get(img_url, stream=True)
            # get img name
            m = re.search('(?:.(?!/))+$', img_url)
            img_name = m.group(0)[1:]
            img_path = os.path.join(save_path, img_name)
            # download image
            if r.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
