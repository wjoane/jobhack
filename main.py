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

unlabeled_data = engine.scrap_site()
# labeled_data = engine.auto_label_data(unlabeled_data)
# model = engine.train_prediction_model(labeled_data)

# url = input("Enter the URL of the page to score: ")
# score = engine.predict_score(url, model)
# print("The predicted score: ", score)
