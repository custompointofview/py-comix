import os
from playwright.sync_api import sync_playwright

import cloudscraper

PAGE_TIMEOUT = 300 * 1000  # 5 min expressed in milliseconds


class SweeperInterface:
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
        # playwright
        self.playwright_context = None
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        if self.playwright_context is None:
            self.playwright_context = sync_playwright()
            self.playwright_context.start()
            self.playwright = self.playwright_context._playwright
            self.browser = self.playwright.chromium.launch(headless=False)

    def stop(self):
        if self.playwright_context is not None:
            self.browser.close()
            self.playwright.stop()
        self.playwright_context = None
        self.playwright = None
        self.browser = None

    def filter_chapters(self):
        print("-" * 75)
        if self.filters is None or len(self.filters) == 0:
            print("# No filters were mentioned")
            return
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
        print("# Chapters were filtered out. Remaining chapters: ")
        for chapter, url in self.chapters.items():
            print("## Chapter:", chapter, " - ", url)

    def announce_url(self):
        print()
        print("=" * 75)
        print("# Going for URL: ", self.main_url)
        print("=" * 75)

    def get_page(self, url, locator=None):
        try:
            if self.browser is None or not self.browser.is_connected():
                self.browser = self.playwright.chromium.launch(headless=False)
            if self.page is None:
                self.page = self.browser.new_page()
            print("- Navigating to URL:", url)
            self.page.goto(url=url, timeout=PAGE_TIMEOUT)

            if self.page.url != url:
                print("- Detected url change...")
                print("- Waiting for page to load...")
                self.page.wait_for_load_state(state="load", timeout=PAGE_TIMEOUT)
                print("- Checking for captcha...")
                self.page.wait_for_timeout(1500)
                captcha = self.page.frame_locator('[title="reCAPTCHA"]').get_by_role(
                    "checkbox", name="I'm not a robot"
                )
                print("- CAPTCHA:", captcha)
                if captcha.is_visible():
                    print("- Found captcha thingy. Trying to click...")
                    captcha.click(
                        button="left",
                        delay=750,
                        position={"x": 10, "y": 10},
                    )
                    self.page.wait_for_timeout(1500)

                    okButton = self.page.locator("#btnSubmit")
                    print("- OK BUTTON:", okButton)
                    if okButton.is_visible():
                        okButton.click(
                            button="left",
                            delay=750,
                            position={"x": 10, "y": 10},
                        )
                        self.page.wait_for_timeout(1500)

            print("- Waiting for URL...")
            self.page.wait_for_url(url=url, timeout=PAGE_TIMEOUT)
            print("- Waiting for page to load...")
            self.page.wait_for_load_state(state="load", timeout=PAGE_TIMEOUT)

            if locator:
                self.page.wait_for_selector(locator, timeout=PAGE_TIMEOUT)
                self.page.locator(locator).focus()

            print("- Page loaded correctly.")
            return self.page
        except Exception as e:
            print("!!! Exception while getting page:", e)
            self.page = None
            self.browser.close()

    def get_name_path(self, dir):
        return os.path.join(dir, self.name)

    def get_chapter_imgs(self, chapter_name):
        return self.chapter_imgs[chapter_name]

    def sweep_collection(self):
        raise NotImplemented("You need a concrete instance and not something abstract.")

    def try_sweep_chapter(self, ch_url, ch_name):
        raise NotImplemented("You need a concrete instance and not something abstract.")

    def close(self):
        if self.scraper:
            self.scraper.close()

    def clean_scraper(self):
        print("### Something went wrong. Cleaning scraper...")
        if self.scraper:
            self.scraper.close()
        self.scraper = cloudscraper.create_scraper()
        if self.proxy_helper:
            self.proxy_helper.reset_current_working_proxy()
