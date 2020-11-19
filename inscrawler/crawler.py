from __future__ import unicode_literals

import glob
import json
import os
import time
from builtins import open
from time import sleep

from tqdm import tqdm

from . import fetch
from . import secret
from .browser import Browser
from .exceptions import RetryException
from .utils import retry


class Logging(object):
    PREFIX = "instagram-crawler"

    def __init__(self):
        try:
            timestamp = int(time.time())

            days = 86400 * 7
            days_ago_log = "/tmp/%s-%s.log" % (Logging.PREFIX, timestamp - days)
            for log in glob.glob("/tmp/instagram-crawler-*.log"):
                if log < days_ago_log:
                    os.remove(log)

            self.logger = open("/tmp/%s-%s.log" % (Logging.PREFIX, timestamp), "w")
            self.log_disable = False
        except Exception:
            self.log_disable = True

    def log(self, msg):
        if self.log_disable:
            return

        self.logger.write(msg + "\n")
        self.logger.flush()

    def __del__(self):
        if self.log_disable:
            return
        self.logger.close()


class InsCrawler(Logging):
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0
        self.login()

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one(".Ls00D .Szr5J")
        if ele_login:
            ele_login.click()

    def login(self):
        browser = self.browser
        url = "%s/accounts/login/" % InsCrawler.URL
        browser.get(url)
        u_input = browser.find_one('input[name="username"]')
        u_input.send_keys(secret.username)
        p_input = browser.find_one('input[name="password"]')
        p_input.send_keys(secret.password)

        login_btn = browser.find_one(".L3NKy")
        login_btn.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_latest_posts_by_tag(self, tag, num):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self.get_post_keys(num)

    def fetch_post(self, key):
        browser = self.browser
        dict_post = {}

        def check_post(key, dict_post):
            browser.get(key)
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")

            # It takes time to load the post for some users with slow network
            if ele_a_datetime is None:
                raise RetryException()

            cur_key = ele_a_datetime.get_attribute("href")
            if key != cur_key:
                raise RetryException()

            dict_post["key"] = cur_key
            fetch.fetch_datetime(browser, dict_post)
            fetch.fetch_caption(browser, dict_post)
            fetch.fetch_location(browser, dict_post)

            self.log(json.dumps(dict_post, ensure_ascii=False))

        try:
            check_post(key, dict_post)

        except Exception:
            return {}

        self.log(json.dumps(dict_post, ensure_ascii=False))

        return dict_post

    def get_post_keys(self, num):
        """
            To get posts, we have to click on the load more
            button and make the browser call post api.
        """
        TIMEOUT = 600
        browser = self.browser
        posts = []
        pre_post_num = 0
        wait_time = 1

        progress_bar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a")[9:]
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in posts:
                    posts.append(key)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                sleep(wait_time)

                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        progress_bar.set_description("fetching_1")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            progress_bar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        progress_bar.close()
        print("Done. Fetched %s posts." % (min(len(posts), num)))
        return posts[:num]
