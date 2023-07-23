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


class SweeperMA(SweeperInterface):
    """
    Sweeper can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    def __init__(self, main_url, dry_run, filters, reverse, use_proxies=True):
        """Initialize the Collector object
        :param main_url: <str> The URL from which to collect chapters and other info
        :param dry_run: <bool> Will only print and not download
        :return: None
        """
        super().__init__(main_url, dry_run, filters, reverse=reverse)

        temp = urlparse(self.main_url)
        self.base_url = str(self.main_url).replace(temp.path, "")
        self.proxy_helper = helpers.HelperProxy()
        self.reverse = reverse
        self.use_proxies = use_proxies
        # LOOK ABOVE TO THE IMPORTS ^
        # self.scraper = cfscrape.create_scraper()
        self.scraper = cloudscraper.create_scraper()

    def sweep(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.announce_url()
        self.sweep_collection()
        self.sweep_chapters()

    def sweep_collection(self) -> None:
        name = None
        html_soup = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            html_soup = self.get_page(self.main_url)
            print("# Finding collection name ...")
            name = html_soup.find("div", class_="story-info-right")
            if name is None:
                print("# Information not found. Retrying...")
                time.sleep(random.uniform(1, 3))
                if i % timeout == 0:
                    self.clean_scraper()
                continue
            break

        if name is None:
            # if name is still not found, retry
            self.clean_scraper()
            self.sweep_collection()

        self.name = str(name.h1.contents[0]).replace("information", "").strip()
        print("## Name:", self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find("ul", class_="row-content-chapter")
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = str(chapter.a["href"]).strip()
                chapter_name = str(chapter.a.contents[0]).strip()
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        self.filter_chapters()
        print("=" * 75)

    def sweep_chapters(self):
        time.sleep(5)
        print("# Chapters info: ")
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc="## Collecting"):
            self.try_sweep_chapter(url, name)

        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print("## {0}: {1} pages".format(chapter, len(imgs)))

    def try_sweep_chapter(self, url, name):
        for i in range(self.RETRY):
            try:
                time.sleep(random.uniform(5, 10))
                self.sweep_chapter(url, name)
            except TimeoutError as e:
                helpers.print_error(e)
                continue
            except LookupError as e:
                helpers.print_error(e)
                print("# Resetting everything and retrying...")
                self.clean_scraper()
                continue
            break

    def clean_scraper(self):
        print("### Something went wrong. Cleaning scraper...")
        self.scraper.close()
        self.scraper = cloudscraper.create_scraper()
        self.proxy_helper.reset_current_working_proxy()

    def sweep_chapter(self, url, chapter_name) -> None:
        # get contents from html
        # print("## CHAPTER:", chapter_name)
        # print("## URL:", url)
        html_soup = self.get_page(url)
        container = html_soup.find("div", class_="container-chapter-reader")
        all_imgs = container.findChildren("img")
        for i, img in enumerate(all_imgs):
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", img["src"])
            self.chapter_imgs[chapter_name].append(img_elem)
        # print("chapters_imgs:", self.chapter_imgs)
