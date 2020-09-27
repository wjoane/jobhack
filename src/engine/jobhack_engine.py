# -----------------------------------------------------------
# This class links multiple components of the AI driven training engine,
# and provides a direct method to scrap a whole site for content, label it,
# train and save a model using the scrapped labeled data.
# It is responsible for implementing the interactions between the components,
# the information flow, and the error handling at a high level.
#
# (C) 2020 Wassim Joane, Mahdia, Tunisia
# email contact@wjoane.me
# -----------------------------------------------------------

from src.lib.classifier.text_classifier import TextClassifier
from src.lib.scrapper.basic_scrapper import BasicScrapper
from src.lib.scrapper.selenium_scrapper import SeleniumScrapper
from src.util.db.mysql_util import MysqlUtil


class JobhackEngine:
    def __init__(self, config, random_ua=False):
        self.__config = config
        self.__classifier = TextClassifier()
        if self.__config['BROWSER'].getboolean('basic_mode'):
            self.__scrapper = BasicScrapper(random_ua=random_ua)
        else:
            self.__scrapper = SeleniumScrapper(self.__config['CHROME'],
                                               random_ua=random_ua)
        self.__content = None

    def scrap_site(self):
        site_url = self.__config['BROWSER']['site_url']
        if not site_url:
            return False

        self.__content = self.__scrapper.start_browsing(
            site_url,
            self.__config['BROWSER']['item_selector'],
            self.__config['BROWSER']['link_selector'],
            max_pages=self.__config['BROWSER'].getint('max_pages')
        )

        db = MysqlUtil(self.__config['DATABASE'])
        db.save(self.__content, truncate=True)

        return self.__content
