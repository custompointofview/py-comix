#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random

from tqdm import tqdm
from urllib.parse import urlparse

import cloudscraper

import helpers

from sweepers.interface import SweeperInterface
from sweepers.utils import add_padding_number

PAGE_TIMEOUT = 300 * 1000  # 5 min expressed in milliseconds

class SweeperMA(SweeperInterface):
    """
    Sweeper can collect chapters, scrape chapter URL and get images
    All will be archived in a temp dir named: archives
    """

    def __init__(self, main_url, dry_run, filters, reverse, start_from, use_proxies=True):
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
        self.save_chapter = None
        self.start_from = start_from

    def sweep(self, save_chapter = None):
        """Collect all chapters and images from chapters
        :return: None
        """
        self.save_chapter = save_chapter
        self.announce_url()
        self.sweep_collection()
        self.sweep_chapters()

    def sweep_collection(self) -> None:
        name = None
        page = None
        timeout = self.RETRY / 5
        for i in range(self.RETRY):
            page = self.get_page(self.main_url)
            page.wait_for_timeout(1000)
            popup_locator = page.locator('.qc-cmp2-summary-buttons')
            if popup_locator.is_visible():
                print("# Popup showed up. Acting on it...")
                popup_locator.last.click()
                page.wait_for_timeout(1000)



            print("# Finding collection name...")
            is_visible = page.is_visible(".story-info-right")
            if not is_visible:
                print("# Information not found. Retrying...")
                time.sleep(random.uniform(1, 3))
                continue

            name = page.locator(".story-info-right").locator('h1').text_content()

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

        self.name = str(name).replace("information", "").strip()
        print("## Name:", self.name)

        print("# Finding chapters ...")
        chapters = page.locator(".row-content-chapter").locator("a").all()
        chapter_index = len(chapters) + 1
        for chapter in chapters:
            chapter_url = chapter.get_attribute("href")
            chapter_name = str(chapter.inner_text()).strip()
            if chapter_name not in self.chapters:
                chapter_index -= 1
                chapter_name = f"{add_padding_number(chapter_index)} - {chapter_name}"
                print("## Chapter: ", chapter_name, " - ", chapter_url)
                self.chapters[chapter_name] = chapter_url
        self.filter_chapters()
        print("=" * 75)

    def sweep_chapters(self):
        time.sleep(5)
        # visit urls and collect img urls
        chapters_list = list(self.chapters.items())
        if (self.reverse):
            print("# Reversing chapters...")
            chapters_list.reverse()
        if (self.start_from):
            print("# Will start from chapter:", self.start_from)
            chapters_list = chapters_list[self.start_from+1:]
        print(f"# Sweeping {len(chapters_list)} chapters...")
        for name, url in tqdm(chapters_list, desc="## Collecting"):
            self.try_sweep_chapter(url, name)
            if self.save_chapter:
                self.save_chapter(name, self.get_chapter_imgs(name))

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
        # print("## CHAPTER:", chapter_name)
        # print("## URL:", url)
        print("### Switching to chapter:", chapter_name)
        page = self.get_page(url)

        print("### Waiting for all pages to load...")
        chapter_container = page.locator(".container-chapter-reader")
        chapter_container.wait_for(timeout=PAGE_TIMEOUT, state="visible")

        all_imgs = chapter_container.locator("img").all()

        print("### Determined number of pages: ", len(all_imgs))
        for i, img in enumerate(all_imgs):
            img.wait_for(timeout=PAGE_TIMEOUT, state="visible")
            time.sleep(0.1)
            img.scroll_into_view_if_needed()
            time.sleep(random.uniform(0.2, 1))
            if chapter_name not in self.chapter_imgs:
                self.chapter_imgs[chapter_name] = []
            img_src = str(img.get_attribute("src")).strip()
            if img_src is not None or img_src != 'None':
                img_elem = (str(i + 1) + ".jpg", img_src)
                print(f"### Page {i+1}:", img_elem)
                self.chapter_imgs[chapter_name].append(img_elem)
