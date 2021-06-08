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

import helpers
from variant import Variant


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
        if variant == Variant.RU:
            return SweeperRU(main_url=self.main_url,
                             dry_run=self.dry_run,
                             filters=self.filters)
        elif variant == Variant.TO:
            return SweeperTO(main_url=self.main_url,
                             dry_run=self.dry_run,
                             filters=self.filters,
                             reverse=self.reverse,
                             use_proxies=self.use_proxies)
        elif variant == Variant.MA:
            return SweeperMA(main_url=self.main_url,
                             dry_run=self.dry_run,
                             filters=self.filters,
                             reverse=self.reverse,
                             use_proxies=self.use_proxies)
        elif variant == Variant.GR:
            return SweeperGR(main_url=self.main_url,
                             dry_run=self.dry_run,
                             filters=self.filters,
                             reverse=self.reverse,
                             use_proxies=self.use_proxies)

    def filter_chapters(self):
        print("-" * 75)
        filtered_out = []
        for chapter, url in self.chapters.items():
            vote_out = True
            for fil in self.filters:
                if str(fil).lower() in str(chapter).lower():
                    vote_out = False
                    break
            if vote_out:
                filtered_out.append(chapter)
        for out in filtered_out:
            if out in self.chapters:
                del self.chapters[out]
        print('# Chapters were filtered out. Remaining chapters: ')
        for chapter, url in self.chapters.items():
            print("### Chapter:", chapter, " - ", url)

    def announce(self):
        print()
        print("=" * 75)
        print("# Going for URL: ", self.main_url)
        print("=" * 75)

    def get_html(self, url):
        response = None
        for i in range(self.RETRY):
            proxy = self.proxy_helper.get_proxy()
            proxies = helpers.PROXY_TEMPLATE.copy()
            for prox in proxies.keys():
                proxies[prox] = proxies[prox].format(proxy=proxy)

            print("### Trying out URL:", url)
            try:
                if self.use_proxies:
                    print("### With proxy:", proxies)
                    response = self.scraper.get(url, timeout=(25, 25), proxies=proxies)
                else:
                    response = self.scraper.get(url, timeout=(25, 25))
            except Exception as e:
                helpers.print_error(e)
                continue

            self.proxy_helper.set_current_working_proxy(proxy)
            break

        if response is not None:
            if not response.ok:
                raise Exception("Book Not Found")
        else:
            raise ConnectionError("Not able to reach url!")
        return bsoup(response.text, 'html.parser')

    def get_name_path(self, dir):
        return os.path.join(dir, self.name)

    def get_chapter_imgs(self, chapter_name):
        return self.chapter_imgs[chapter_name]

    def sweep_collection(self):
        raise NotImplemented("You need a concrete instance and not something abstract.")

    def try_sweep_chapter(self, churl, chname):
        raise NotImplemented("You need a concrete instance and not something abstract.")

    def close(self):
        self.scraper.close()
        self.scraper.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.scraper.close()
        self.scraper.quit()


class SweeperRU(SweeperFactory):
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
            time.sleep(random.uniform(1, 5))
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

    try_sweep_chapter = sweep_chapter


class SweeperTO(SweeperFactory):
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
        self.base_url = str(self.main_url).replace(temp.path, '')
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
        self.announce()
        self.sweep_collection()
        self.sweep_chapters()

    def sweep_collection(self) -> None:
        name = None
        html_soup = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            html_soup = self.get_html(self.main_url)
            print("# Finding collection name ...")
            name = html_soup.find('div', class_='barTitle')
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

        self.name = str(name.contents[0]).replace('information', '').strip()
        print('## Name:', self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find('table', class_='listing')
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = self.base_url + \
                              str(chapter.a['href']).strip() + "&readType=1&quality=hq"
                chapter_name = str(chapter.a.contents[0]).strip()
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        self.filter_chapters()
        print("=" * 75)

    def sweep_chapters(self):
        time.sleep(5)
        print('# Chapters info: ')
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc='## Collecting'):
            self.try_sweep_chapter(url, name)

        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print('## {0}: {1} pages'.format(chapter, len(imgs)))

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
        html_soup = self.get_html(url)
        js_text = html_soup.findAll("script", type="text/javascript")
        regex = re.compile('lstImages.push\("(.*)"\);')

        page_list = None
        for script in js_text:
            try:
                page_list = regex.findall(str(script))
            except IndexError:
                raise Exception(
                    'There is something wrong with page Javascript! Probably a wild Captcha appeared...')
            if len(page_list) > 0:
                break
        if len(page_list) == 0:
            # print('-' * 75 + 'JAVASCRIPT FINDINGS')
            # print(js_text)
            # print('-' * 75 + 'HTML RESULT')
            # print(html_soup)
            # print('-' * 75)
            raise LookupError(
                'Nothing was found! Probably a wild Captcha appeared...')

        for i, page in enumerate(page_list):
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", page)
            self.chapter_imgs[chapter_name].append(img_elem)


class SweeperMA(SweeperFactory):
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
        self.base_url = str(self.main_url).replace(temp.path, '')
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
        self.announce()
        self.sweep_collection()
        self.sweep_chapters()

    def sweep_collection(self) -> None:
        name = None
        html_soup = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            html_soup = self.get_html(self.main_url)
            print("# Finding collection name ...")
            name = html_soup.find('div', class_='story-info-right')
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

        self.name = str(name.h1.contents[0]).replace('information', '').strip()
        print('## Name:', self.name)

        print("# Finding chapters ...")
        chapters = html_soup.find('ul', class_='row-content-chapter')
        for chapter in chapters.findChildren():
            if chapter.a:
                chapter_url = str(chapter.a['href']).strip()
                chapter_name = str(chapter.a.contents[0]).strip()
                if chapter_name not in self.chapters:
                    print("## Chapter: ", chapter_name, " - ", chapter_url)
                    self.chapters[chapter_name] = chapter_url
        self.filter_chapters()
        print("=" * 75)

    def sweep_chapters(self):
        time.sleep(5)
        print('# Chapters info: ')
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc='## Collecting'):
            self.try_sweep_chapter(url, name)

        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print('## {0}: {1} pages'.format(chapter, len(imgs)))

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
        html_soup = self.get_html(url)
        container = html_soup.find('div', class_='container-chapter-reader')
        all_imgs = container.findChildren("img")
        for i, img in enumerate(all_imgs):
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", img['src'])
            self.chapter_imgs[chapter_name].append(img_elem)
        # print("chapters_imgs:", self.chapter_imgs)


class SweeperGR(SweeperFactory):
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
        self.base_url = str(self.main_url).replace(temp.path, '')
        self.proxy_helper = helpers.HelperProxy()
        self.reverse = reverse
        self.use_proxies = use_proxies
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.scraper = webdriver.Chrome(options=options)

    def sweep(self):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.announce()
        self.sweep_collection()
        self.sweep_chapters()

    def get_html(self, url):
        response = None
        for i in range(self.RETRY):
            print("### Trying out URL:", url)
            try:
                self.scraper.get(url)
                time.sleep(random.uniform(1, 3))
                response = self.scraper.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            except Exception as e:
                helpers.print_error(e)
                continue
            break

        if response is None or response == '':
            raise ConnectionError("Not able to reach url!")
        return bsoup(response, 'html.parser')

    def sweep_collection(self) -> None:
        name = None
        html_soup = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            html_soup = self.get_html(self.main_url)
            print("# Finding collection name ...")
            name = html_soup.find('div', class_='top-texts ng-star-inserted')
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
        print('## Name:', self.name)

        print("# Finding chapters ...")
        container = html_soup.find('div', class_='left-side ng-star-inserted')
        chapters = container.findAll("a", class_='issue-title ng-star-inserted', recursive=True,
                                     href=True)
        for chapter in chapters:
            chapter_url = str(chapter['href']).strip()
            chapter_url = self.base_url + chapter_url
            chapter_name = str(chapter.contents[0]).strip()
            if chapter_name not in self.chapters:
                print("## Chapter: ", chapter_name, " - ", chapter_url)
                self.chapters[chapter_name] = chapter_url

        self.filter_chapters()
        print("=" * 75)

    def sweep_chapters(self):
        time.sleep(5)
        print('# Chapters info: ')
        # visit urls and collect img urls
        for name, url in tqdm(self.chapters.items(), desc='## Collecting'):
            self.try_sweep_chapter(url, name)

        # print chapter info
        for chapter, imgs in self.chapter_imgs.items():
            print('## {0}: {1} pages'.format(chapter, len(imgs)))

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
        # print("## CHAPTER:", chapter_name)
        # print("## URL:", url)
        html_soup = self.get_html(url)
        container = html_soup.find('div', class_='slides-container ads')
        all_pages = container.findChildren("div", class_="page-container ng-star-inserted")
        for i, page in tqdm(enumerate(all_pages), desc="### Gathering images"):
            # move to the page so that the javascript can load target
            element_id = 'page_' + str(i)
            element = self.scraper.find_element_by_id(element_id)
            actions = webdriver.ActionChains(self.scraper)
            actions.move_to_element(element).perform()
            new_img = None
            for x in range(100):
                # wait for load to finish
                time.sleep(0.5)
                # get new version after scroll
                response = self.scraper.execute_script(
                    "return document.getElementById('{0}').innerHTML".format(element_id))
                new_page = bsoup(response, 'html.parser')
                # print("NEW PAGE:", new_page)
                # get image element
                new_img = new_page.find('img')
                # print("NEW IMG:", new_img)
                if new_img is not None:
                    break

            img_src = new_img['src'].replace("thumbnail", "image")
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_elem = (str(i + 1) + ".jpg", img_src)
            self.chapter_imgs[chapter_name].append(img_elem)

    def clean_scraper(self):
        print("### Something went wrong. Cleaning scraper...")
        self.scraper.quit()
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        self.scraper = webdriver.Chrome(options=options)
