#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import random

import requests as req

from tqdm import tqdm
from bs4 import BeautifulSoup as bsoup

import cfscrape
from urllib.parse import urlparse


class Sweeper:
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
        super().__init__()
        self.main_url = main_url
        self.dry_run = dry_run
        self.name = None
        self.chapters = {}
        self.chapter_imgs = {}
        self.filters = filters

    def filter_chapters(self):
        filtered_out = []
        for fil in self.filters:
            for chapter, url in self.chapters.items():
                if str(fil).lower() not in str(chapter).lower():
                    filtered_out.append(chapter)
        for out in filtered_out:
            del self.chapters[out]
        print('# Chapters were filtered out.')


class SweeperRU(Sweeper):
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

    def sweep(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.sweep_collection()
        # self.sweep_chapters()

    def sweep_collection(self) -> None:
        print("=" * 75)

        response = req.get(self.main_url)
        html_soup = bsoup(response.text, 'html.parser')

        print("# Finding collection name ...")
        name = html_soup.find('h2', class_='listmanga-header')
        self.name = str(name.contents[0]).strip()
        print('## Name:', self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find('ul', class_='chapters')
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = chapter.a['href']
                chapter_name = chapter.a.contents[0]
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        print("=" * 75)
        self.filter_chapters()

    def sweep_chapters(self):
        time.sleep(random.uniform(0, 5))
        print('# Chapters info: ')
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc='## Collecting'):
            time.sleep(random.uniform(0, 5))
            self.sweep_chapter(url, name)
        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print('## {0}: {1} pages'.format(chapter, len(imgs)))

    def sweep_chapter(self, url, chapter_name) -> None:
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


class SweeperTO(Sweeper):
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

        temp = urlparse(self.main_url)
        self.base_url = str(self.main_url).replace(temp.path, '')
        self.scraper = cfscrape.create_scraper()

    def sweep(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.sweep_collection()
        self.sweep_chapters()

    def get_html(self, url):
        response = self.scraper.get(url)
        if not response.ok:
            raise Exception("Book Not Found")
        return bsoup(response.text, 'html.parser')

    def sweep_collection(self) -> None:
        print("=" * 75)
        html_soup = self.get_html(self.main_url)

        print("# Finding collection name ...")
        name = html_soup.find('div', class_='barTitle')
        self.name = str(name.contents[0]).replace('information', '').strip()
        print('## Name:', self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find('table', class_='listing')
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = self.base_url + str(chapter.a['href']).strip() + "&readType=1&quality=hq"
                chapter_name = str(chapter.a.contents[0]).strip()
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        print("=" * 75)
        self.filter_chapters()

    def sweep_chapters(self):
        time.sleep(5)
        print('# Chapters info: ')
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc='## Collecting'):
            time.sleep(random.uniform(1, 5))
            self.sweep_chapter(url, name)
        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print('## {0}: {1} pages'.format(chapter, len(imgs)))

    def sweep_chapter(self, url, chapter_name) -> None:
        # get contents from html
        html_soup = self.get_html(url)
        js_text = html_soup.findAll("script", type="text/javascript")
        regex = re.compile('lstImages.push\("(.*)"\);')

        page_list = None
        for script in js_text:
            try:
                page_list = regex.findall(script.text)
            except IndexError:
                raise Exception('There is something wrong with page Javascript! Probably a wild Captcha appeared...')
            if len(page_list) > 0:
                break
        if len(page_list) == 0:
            print('-'*75)
            print(html_soup)
            print('-'*75)
            raise Exception('Nothing was found! Probably a wild Captcha appeared...')

        for i, page in enumerate(page_list):
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", page)
            self.chapter_imgs[chapter_name].append(img_elem)
