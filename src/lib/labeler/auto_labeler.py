from fuzzysearch import find_near_matches
from unidecode import unidecode
import logging


class AutoLabeler:
    def __init__(self, config):
        self.__config = config

    def label_data_with_keywords(self, data):
        keywords_plus = self.__config['positive_keywords'].split(',')
        keywords_minus = self.__config['negative_keywords'].split(',')
        for page in data:
            logging.debug("Labeling page: " + page['url'])
            if page['code'] < 300:
                plus_score = self.__score_text_with_keywords(
                    page['content'], keywords_plus)
                minus_score = self.__score_text_with_keywords(
                    page['content'], keywords_minus) if keywords_minus else 0
                page['label'] = (plus_score - self.__config.getfloat(
                    'negative_weight') * minus_score) / 100
            else:
                page['label'] = 0
            yield page

    def __score_text_with_keywords(self, text, keywords):
        matches = 0
        for word in keywords:
            hits = find_near_matches(
                word, unidecode(text).lower(),
                max_l_dist=max(0, len(word) - self.__config.getint(
                    'min_l_fuzzy')) // self.__config.getint('max_l_divider'))
            matches += len(hits) + (self.__config.getint(
                'bonus_for_hits') if len(hits) > 0 else 0)
        return matches
