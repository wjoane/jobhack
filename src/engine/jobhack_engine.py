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
        self.__model = None
        if self.__config['DATABASE']['type'] == 'mysql':
            self.__db = MysqlUtil(self.__config['DATABASE'])

    def scrap_site(self, continue_from=False):
        site_url = self.__config['WEBSITE']['site_url']
        if not site_url:
            return False

        data_generator = self.__scrapper.start_browsing(
            site_url,
            self.__config['WEBSITE']['item_selector'],
            self.__config['WEBSITE']['link_selector'],
            description_selector=self.__config['WEBSITE'][
                'description_selector'],
            start_page=(continue_from if continue_from else
                        self.__config['WEBSITE'].getint('start_page')),
            max_pages=self.__config['WEBSITE'].getint('max_pages'),
            relative_links=self.__config['WEBSITE'].getboolean(
                'relative_links'),
            lang=self.__config['WEBSITE']['language']
        )

        if self.__db is not None:
            self.__data_set = self.__db.save(data_generator,
                                             truncate=not continue_from)
        else:
            self.__data_set = data_generator

        return self.__data_set

    def retry_failed_pages(self, unlabeled_data=None):
        data_set = unlabeled_data
        if not data_set:
            data_set = self.__data_set
        if not data_set and self.__db is not None:
            data_set = self.__db.load()
        if not data_set:
            return False

        self.__data_set = self.__scrap_failed_pages(data_set)
        if not unlabeled_data and self.__db is not None:
            self.__data_set = self.__db.update_by_url(self.__data_set)

        return self.__data_set

    def __scrap_failed_pages(self, data_set):
        for page in data_set:
            if page['code'] >= 300:
                new_page = self.__scrapper.parse_page_content(
                    page['url'], description_selector=self.__config[
                        'WEBSITE']['description_selector'])
                new_page['update'] = True
                yield new_page
            else:
                page['update'] = False
                yield page

    def auto_label_data(self, unlabeled_data=None):
        data_set = unlabeled_data
        if not data_set and self.__data_set:
            data_set = self.__data_set
        if not data_set and self.__db is not None:
            data_set = self.__db.load()
        if not data_set:
            return False

        self.__data_set = self.__labeler.label_data_with_keywords(data_set)

        if not unlabeled_data and self.__db is not None:
            self.__data_set = self.__db.update_labels(self.__data_set)

        return self.__data_set

    def train_prediction_model(self, labeled_data=None):
        data_set = labeled_data
        if not data_set and self.__data_set:
            self.__data_set = [page for page in self.__data_set
                               if page['code'] == 200]
            data_set = self.__data_set
        if not data_set and self.__db is not None:
            data_set = list(self.__db.load(200))
        if not data_set:
            return False

        slice_size = (len(data_set) * self.__config['TRAINING'].getint(
            'training_percent')) // 200
        data_set = data_set[:slice_size] + data_set[-slice_size:]
        self.__classifier.train(data_set, self.__config['TRAINING'])
        self.__classifier.dump_model_to_file(
            self.__config['TRAINING']['model_path'])
        self.__classifier.dump_data_to_csv(
            self.__config['TRAINING']['csv_data_path'])

        return self.__classifier

    def predict_score(self, url, text_classifier=None):
        classifier = text_classifier
        if not classifier and self.__classifier:
            if not self.__classifier.is_trained:
                self.__classifier.load_model_from_file(
                    self.__config['TRAINING']['model_path'])
            classifier = self.__classifier

        page = self.__scrapper.parse_page_content(
            url, lang=self.__config['WEBSITE']['language'])

        page['prediction'] = classifier.predict_proba(page['content'])

        return page
