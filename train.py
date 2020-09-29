import configparser
import logging

from src.engine.jobhack_engine import JobhackEngine

config = configparser.ConfigParser()
config.read('config.ini')

# noinspection PyArgumentList
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('jobhack.log'),
        logging.StreamHandler()
    ])

engine = JobhackEngine(config, random_ua=False)

# TODO Implement --continue from page argument option
engine.scrap_site()
for _ in range(3):
    engine.retry_failed_pages()
engine.auto_label_data()
engine.train_prediction_model()
