import logging
import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from fake_useragent import UserAgent
from langdetect import detect


class BasicScrapper:
    def __init__(self, random_ua=False):
        logging.info('Initiating basic curl request agent')
        if random_ua:
            ua = UserAgent()
            user_agent = ua.random
        else:
            user_agent = 'curl/7.68.0'
        headers = {
            'user-agent': user_agent,
            'referrer': "https://google.com",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': '*',
            'accept-language': 'en,de;q=0.9,fr;q=0.8',
            'pragma': 'no-cache'
        }
        self.__session = requests.Session()
        self.__session.headers.update(headers)

    def start_browsing(
            self, home_url, item_selector, link_selector,
            description_selector=None, max_pages=1, start_page=1,
            relative_links=False):
        domain = re.search('https?://([A-Za-z_0-9.-]+).*', home_url).group(1)
        logging.info('Crawling through ' + domain)
        progress = start_page
        for page_number in range(start_page, max_pages + 1):
            try:
                req = self.__session.get(home_url.replace(
                    '<#>', str(page_number)))
                soup = BeautifulSoup(req.text, 'html.parser')
            except Exception as e:
                logging.error("Unable to browse page #" + str(page_number))
                logging.error(str(e))
                continue

            items_links = soup.select(item_selector)

            links = []
            for item in items_links:
                try:
                    links.append(item.select_one(link_selector).get('href'))
                except Exception as e:
                    logging.warning("Unable to select link by CSS selector")
                    logging.warning(str(e))

            for link in links:
                page_text = self.parse_page_content(
                    ('https://' + domain if relative_links else '') + link,
                    description_selector)
                if page_text:
                    yield page_text

            logging.info(str(progress * 100 // max_pages) +
                         '% | ' + home_url.replace('<#>', str(page_number)))
            progress += 1

        logging.info('Scrapping completed ' + domain)

    def parse_page_content(self, page_url, description_selector=None):
        logging.debug('Parsing page: ' + page_url)
        try:
            req = self.__session.get(page_url)
            soup = BeautifulSoup(req.text, 'html.parser')
        except Exception as e:
            logging.error("Unable to reach page " + page_url)
            logging.error(str(e))
            return {
                'url': page_url,
                'selector': description_selector,
                'code': 400,  # Bad Request
                'content': '400: Basic Scrapper unable to reach page',
            }

        if req.status_code != 200:
            description_selector = None

        if description_selector is None:
            html = req.text
        else:
            try:
                html = soup.select_one(
                    description_selector).encode_contents()
            except Exception as e:
                logging.error(
                    "Unable to select job description by CSS selector")
                logging.error(str(e))
                description_selector = 'invalid'
                html = req.text

        text = self._mine_text_from_html(html)

        if req.status_code != 200:
            return {
                'url': page_url,
                'selector': description_selector,
                'code': req.status_code,
                'content': text,
            }

        return {
            'url': page_url,
            'selector': description_selector,
            'code': self._detect_response_error(text),
            'content': text
        }

    def _mine_text_from_html(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.__tag_visible, texts)
        return re.sub('\\s+', ' ', u" ".join(t.strip() for t in visible_texts))

    def __tag_visible(self, element):
        hidden_tags = ['style', 'script', 'head', 'title', 'meta', 'a']
        try:
            if isinstance(element, Comment):
                return False
            if element.parent.name in hidden_tags:
                return False
            if element.parent.parent.name in hidden_tags:
                return False
            if element.parent.parent.parent.name in hidden_tags:
                return False
        except AttributeError:
            pass
        return True

    def _detect_response_error(self, text, lang=None):
        ERROR_KEYWORDS = ['found', 'forbidd', 'authoriz', 'invalid', 'fail',
                          'allow', 'error', 'denied', 'block', 'security',
                          'incident', 'request', 'unsuccessful', 'access']
        if len(text) < 10:
            return 204  # No Content
        if len(text) < 200:
            lo_txt = text.lower()
            if len([word for word in ERROR_KEYWORDS if word in lo_txt]) > 0:
                return 403  # Forbidden
            return 206  # Partial Content
        if (lang is not None) and (detect(text) != lang):
            return 215  # Wrong language
        return 200  # OK
