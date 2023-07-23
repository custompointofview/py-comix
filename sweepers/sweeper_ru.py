#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import random

import requests as req
from tqdm import tqdm
from bs4 import BeautifulSoup as bsoup
from urllib.parse import urlparse

import cloudscraper
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import helpers
from variant import Variant

from sweepers.interface import SweeperInterface


class SweeperRU(SweeperInterface):
    """
    Sweeper can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    def __init__(self, main_url, dry_run, filters):
        """Initialize the Collector object
        :param main_url: <str> The URL from which to collect chapters and other info
        :param dry_run: <bool> Will only print and not download
        :return: None
        """
        super().__init__(main_url, dry_run, filters)

    def sweep_collection(self) -> None:
        print("=" * 75)

        response = req.get(self.main_url)
        html_soup = bsoup(response.text, "html.parser")

        print("# Finding collection name ...")
        name = html_soup.find("h2", class_="listmanga-header")
        self.name = str(name.contents[0]).strip()
        print("## Name:", self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find("ul", class_="chapters")
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = chapter.a["href"]
                chapter_name = chapter.a.contents[0]
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        print("=" * 75)
        self.filter_chapters()

    def sweep_chapters(self):
        time.sleep(random.uniform(0, 5))
        print("# Chapters info: ")

        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc="## Collecting"):
            time.sleep(random.uniform(1, 5))
            self.sweep_chapter(url, name)
        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print("## {0}: {1} pages".format(chapter, len(imgs)))

    def sweep_chapter(self, url, chapter_name) -> None:
        # get contents from html
        respose = req.get(url)
        html_soup = bsoup(respose.text, "html.parser")
        img_tags = html_soup.find("div", id="all")
        img_list = list(img_tags.findChildren())
        for img_tag in img_list:
            img_url = str(img_tag["data-src"]).strip()
            m = re.search("(?:.(?!/))+$", img_url)
            img_name = m.group(0)[1:]
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (img_name, img_url)
            self.chapter_imgs[chapter_name].append(img_elem)

    try_sweep_chapter = sweep_chapter
