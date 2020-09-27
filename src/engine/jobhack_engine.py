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
from src.lib.labeler.auto_labeler import AutoLabeler
from src.lib.scrapper.basic_scrapper import BasicScrapper
from src.lib.scrapper.selenium_scrapper import SeleniumScrapper
from src.util.db.mysql_util import MysqlUtil


class JobhackEngine:
    def __init__(self, config, random_ua=False):
        self.__config = config
        self.__classifier = TextClassifier()
        self.__labeler = AutoLabeler(self.__config['LABELER'])
        if self.__config['WEBSITE'].getboolean('basic_mode'):
            self.__scrapper = BasicScrapper(random_ua=random_ua)
        else:
            self.__scrapper = SeleniumScrapper(self.__config['CHROME'],
                                               random_ua=random_ua)
        self.__data_set = None
        if self.__config['DATABASE']['type'] == 'mysql':
            self.__db = MysqlUtil(self.__config['DATABASE'])

    def scrap_site(self):
        site_url = self.__config['WEBSITE']['site_url']
        if not site_url:
            return False

        self.__data_set = self.__scrapper.start_browsing(
            site_url,
            self.__config['WEBSITE']['item_selector'],
            self.__config['WEBSITE']['link_selector'],
            description_selector=self.__config['WEBSITE'][
                'description_selector'],
            start_page=self.__config['WEBSITE'].getint('start_page'),
            max_pages=self.__config['WEBSITE'].getint('max_pages'),
            relative_links=self.__config['WEBSITE'].getboolean(
                'relative_links'),
            lang=self.__config['WEBSITE']['language']
        )

        if self.__db:
            self.__db.save(self.__data_set, truncate=True)

        return self.__data_set

    def retry_failed_pages(self, unlabeled_data=None):
        data_set = unlabeled_data
        if not data_set:
            data_set = self.__data_set
        if not data_set and self.__db:
            data_set = self.__db.load

        failed_pages = self.__scrap_failed_pages(data_set)
        if not unlabeled_data and self.__db:
            self.__db.update_by_url(failed_pages)

        self.__data_set = [page if page['code'] == 200 else next(
            item for item in failed_pages if item['url'] == page['url'])
                           for page in data_set]

        return self.__data_set

    def __scrap_failed_pages(self, data_set):
        for page in data_set:
            if page['code'] != 200:
                yield self.__scrapper.parse_page_content(
                    page['url'], description_selector=self.__config[
                        'WEBSITE']['description_selector'])

    def auto_label_data(self, unlabeled_data=None):
        data_set = unlabeled_data
        if not data_set:
            data_set = self.__data_set
        if not data_set and self.__db:
            data_set = self.__db.load

        self.__data_set = self.__labeler.label_data_with_keywords(data_set)

        if not unlabeled_data and self.__db:
            self.__db.update_labels(self.__data_set)

        return self.__data_set
