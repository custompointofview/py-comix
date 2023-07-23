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


class SweeperGR(SweeperInterface):
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
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        self.scraper = webdriver.Chrome(options=options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.scraper.close()
        self.scraper.quit()

    def sweep(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.announce_url()
        self.sweep_collection()
        self.sweep_chapters()

    def get_page(self, url):
        response = None
        for i in range(self.RETRY):
            print("### Trying out URL:", url)
            try:
                self.scraper.get(url)
                time.sleep(random.uniform(1, 3))
                response = self.scraper.execute_script(
                    "return document.getElementsByTagName('html')[0].innerHTML"
                )
            except Exception as e:
                helpers.print_error(e)
                continue
            break

        if response is None or response == "":
            raise ConnectionError("Not able to reach url!")
        return bsoup(response, "html.parser")

    def sweep_collection(self) -> None:
        name = None
        html_soup = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            html_soup = self.get_page(self.main_url)
            print("# Finding collection name ...")
            name = html_soup.find("div", class_="top-texts ng-star-inserted")
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

        self.name = str(name.h1.contents[0]).strip()
        print("## Name:", self.name)

        print("# Finding chapters ...")
        container = html_soup.find("div", class_="left-side ng-star-inserted")
        chapters = container.findAll(
            "a", class_="issue-title ng-star-inserted", recursive=True, href=True
        )
        for chapter in chapters:
            chapter_url = str(chapter["href"]).strip()
            chapter_url = self.base_url + chapter_url
            chapter_name = str(chapter.contents[0]).strip()
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

    def sweep_chapter(self, url, chapter_name) -> None:
        # get contents from html
        html_soup = self.get_page(url)
        container = html_soup.find("div", class_="slides-container ads")
        all_pages = container.findChildren(
            "div", class_="page-container ng-star-inserted"
        )
        # scroll controller
        for i, page in enumerate(
            tqdm(all_pages, desc="### Gathering images", ascii=True)
        ):
            # move to the page so that the javascript can load target
            element_id = "page_" + str(i)
            self._scroll_to_element_by_id(element_id)
            # start gathering
            new_img = None
            for x in range(100):
                # get new version after scroll
                response = self.scraper.execute_script(
                    "return document.getElementById('{0}').innerHTML".format(element_id)
                )
                new_page = bsoup(response, "html.parser")
                # get image element
                new_img = new_page.find("img")
                # print("NEW IMG:", new_img)
                if new_img is not None:
                    break
                # re-scroll
                if x % 10 == 0 and x != 0:
                    self._scroll_to_element_by_id("page_0")
                    self._scroll_to_element_by_id(element_id)
                # wait for load to finish
                time.sleep(random.uniform(0.5, 1))

            img_src = new_img["src"].replace("thumbnail", "image")
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", img_src)
            self.chapter_imgs[chapter_name].append(img_elem)

    def _scroll_to_element_by_id(self, element_id):
        element = self.scraper.find_element_by_id(element_id)
        # actions way
        actions = webdriver.ActionChains(self.scraper)
        actions.move_to_element(element).perform()
        # other way
        # self.scraper.execute_script('arguments[0].scrollIntoView(true);', element)
        # scroll_position = self.scraper.execute_script('return window.pageYOffset;')
        time.sleep(2)

    def clean_scraper(self):
        print("### Something went wrong. Cleaning scraper...")
        self.scraper.quit()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.scraper = webdriver.Chrome(options=options)
