import logging
import re
from random import randint, random
from time import sleep

from fake_useragent import UserAgent
from selenium import webdriver

from src.lib.scrapper.basic_scrapper import BasicScrapper


class SeleniumScrapper(BasicScrapper):
    def __init__(self, chrome_config, random_ua=True, headless=True):
        logging.info('Initiating selenium browser')
        self.__driver = chrome_config['driver']
        self.__options = webdriver.ChromeOptions()
        self.__options.binary_location = chrome_config['bin']
        self.__options.headless = False
        self.__options.add_argument("--window-size=1920,1200")
        self.__options.add_argument("--disable-dev-shm-usage")
        self.__options.add_argument("--no-sandbox")
        self.__options.add_argument(
            "--user-data-dir=" + chrome_config['profile'])
        if random_ua:
            ua = UserAgent()
            user_agent = ua.random
        else:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                         "AppleWebK it/537.36 (KHTML, like Gecko) " \
                         "Chrome/84.0.4147.125 Safari/537.36"
        self.__options.add_argument(f'user-agent={user_agent}')

    def start_browsing(
            self, home_url, item_selector, link_selector,
            description_selector=None, max_pages=1, start_page=1,
            relative_links=False, sleepy=True):
        domain = re.search('https?://([A-Za-z_0-9.-]+).*', home_url).group(1)
        logging.info('Crawling through ' + domain)
        progress = start_page
        for page_number in range(start_page, max_pages + 1):
            driver = webdriver.Chrome(
                options=self.__options, executable_path=self.__driver)
            try:
                driver.get(home_url.replace('<#>', str(page_number)))
            except Exception as e:
                logging.error("Unable to browse page #" + str(page_number))
                logging.error(str(e))
                driver.quit()
                continue
            if sleepy:
                sleep(randint(50, 200) / 10)

            try:
                items_links = driver.find_elements_by_css_selector(
                    item_selector)
            except Exception as e:
                logging.warning("Unable to select items by CSS selector")
                logging.warning(str(e))
                driver.quit()
                continue

            links = []
            for item in items_links:
                try:
                    links.append(item.find_element_by_css_selector(
                        link_selector).get_attribute('href'))
                except Exception as e:
                    logging.error("Unable to select link by CSS selector")
                    logging.error(str(e))

            for link in links:
                if random() > 0.5:
                    page_text = self.parse_page_content(
                        ('https://' + domain if relative_links else '') + link,
                        description_selector)
                    if sleepy:
                        sleep(randint(10, 50) / 10)
                    if page_text:
                        yield page_text
                else:
                    logging.debug("Skipping " + link)

            logging.info(str(progress * 100 // max_pages) +
                         '% | ' + home_url.replace('<#>', str(page_number)))
            progress += 1
            driver.quit()

        logging.info('Scrapping completed ' + domain)

    def parse_page_content(self, page_url, description_selector=None):
        logging.debug('Parsing ' + page_url)
        try:
            driver = webdriver.Chrome(
                options=self.__options, executable_path=self.__driver)
        except Exception as e:
            logging.error("Unable to reach browser " + page_url)
            logging.error(str(e))
            return {
                'url': page_url,
                'selector': description_selector,
                'code': 500,  # Server Error
                'content': '500: Basic Scrapper unable to start browser',
            }
        try:
            driver.get(page_url)
        except Exception as e:
            logging.error("Unable to reach page " + page_url)
            logging.error(str(e))
            driver.quit()
            return {
                'url': page_url,
                'selector': description_selector,
                'code': 400,  # Bad Request
                'content': '400: Selenium Scrapper unable to reach page',
            }

        if description_selector is None:
            html = driver.page_source
        else:
            try:
                html = driver.find_element_by_css_selector(
                    description_selector).get_attribute('innerHTML')
            except Exception as e:
                logging.error(
                    "Unable to select job description by CSS selector")
                logging.error(str(e))
                description_selector = 'invalid'
                html = driver.page_source

        text = self._mine_text_from_html(html)
        driver.quit()
        return {
            'url': page_url,
            'selector': description_selector,
            'code': self._detect_response_error(text),
            'content': text
        }
