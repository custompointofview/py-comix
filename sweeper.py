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


class Sweeper:
    """
    Sweeper can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

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
        self.chapter_imgs = {}

    def sweep(self, dest_dir):
        """Collect all chapters and images from chapters
        :param dest_dir: <string> Path where all files will be saved
        :return: None
        """
        # collect chapter urls
        self.sweep_collection()
        # visit urls and collect images
        for name, url in self.chapters.items():
            time.sleep(random.uniform(0, 0.5))
            self.sweep_chapter(url, name)

    def sweep_collection(self) -> None:
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

    def sweep_chapter(self, url, chapter_name) -> None:
        print('# Gathering chapter: ', chapter_name)
        # get contents from html
        respose = req.get(url)
        html_soup = bsoup(respose.text, 'html.parser')
        img_tags = html_soup.find('div', id='all')
        img_list = list(img_tags.findChildren())
        for img_tag in img_list:
            img_url = str(img_tag['data-src']).strip()
            m = re.search('(?:.(?!/))+$', img_url)
            img_name = m.group(0)[1:]

            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (img_name, img_url)
            self.chapter_imgs[chapter_name].append(img_elem)
