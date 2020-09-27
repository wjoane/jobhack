import re
import pickle
import logging
import pandas as pd
from unidecode import unidecode as dc
from nltk.stem.snowball import FrenchStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class TextClassifier:
    def __init__(self):
        self.__stemmer = FrenchStemmer()

    def train(self, data, options):
        logging.info(f'Training new model with {len(data)} examples...')
        if options['preprocessed']:
            self.__training_data = data
        else:
            self.__training_data = self.preprocess_data_set(data)

        features, self.__vectorizer = self.__extract_features(
            options['max_features'], options['min_df'], options['max_df'])
        logging.info("Features extracted: " +
                     str(len(self.__vectorizer.get_feature_names())))

        X = features.toarray()
        y = self.__training_data['labels'].to_list()
        y = [True if score > options['class_threshold'] else False
             for score in y]

        self.__model = LogisticRegression()
        logging.info('Model fitting: ' + str(type(self.__model)))
        self.__model.fit(X, y)
        return self.__model

    def predict(self, text):
        preprocessed_text = self.__preprocess_text_string(text)
        feature_vector = self.__vectorizer.transform([preprocessed_text])
        return self.__model.predict(feature_vector)[0]

    def predict_proba(self, text):
        preprocessed_text = self.__preprocess_text_string(text)
        feature_vector = self.__vectorizer.transform([preprocessed_text])
        return self.__model.predict_proba(feature_vector)[0][1]

    def predict_list(self, text_list):
        preprocessed_text_list = [
            self.__preprocess_text_string(text) for text in text_list]
        feature_vector = self.__vectorizer.transform(preprocessed_text_list)
        return self.__model.predict(feature_vector)

    def predict_list_proba(self, text_list):
        preprocessed_text_list = [
            self.__preprocess_text_string(text) for text in text_list]
        feature_vector = self.__vectorizer.transform(preprocessed_text_list)
        return self.__model.predict_proba(feature_vector)

    def dump_model_to_file(self, path):
        with open(path, 'wb') as file:
            pickle.dump({
                'vectorizer': self.__vectorizer,
                'model': self.__model
            }, file)
        return path

    def load_model_from_file(self, path):
        logging.info('Loading pretrained classification model...')
        with open(path, 'rb') as file:
            loaded = pickle.load(file)
            self.__vectorizer = loaded['vectorizer']
            self.__model = loaded['model']
        return self.__model, self.__vectorizer

    def dump_data_to_csv(self, path):
        self.__training_data.to_csv(path, index=False)

    def __extract_features(self, max_features, min_df, max_df):
        vectorizer = TfidfVectorizer(max_features=max_features, min_df=min_df,
                                     max_df=max_df)
        tfidf = vectorizer.fit_transform(
            self.__training_data['text'].to_list())

        return tfidf, vectorizer

    def preprocess_data_set(self, data):
        logging.info(f'Preprecessing data, {len(data)} examples...')
        preprocessed_data = []
        for row in data:
            content = row['content'].decode("utf-8")
            content = self.__preprocess_text_string(content)
            preprocessed_data.append({
                'text': content,
                'label': row['label']})

        df = pd.DataFrame(preprocessed_data)
        df = df.drop_duplicates(subset='text')
        df = df.sort_values(by=['label'])
        return df

    def __preprocess_text_string(self, content):
        # Remove accents
        content = dc(content)

        # Lower case only
        content = content.lower()

        # Remove special characters and numbers
        content = re.sub(r'[^a-z\s\-]+', ' ', content)
        content = re.sub(r'[\-]+', '', content)

        # Stem each word
        words = content.split()
        words = [self.__stemmer.stem(word) for word in words]
        content = ' '.join(words)

        # Remove too short stems
        content = f" {content} "
        content = re.sub(r'\W*\b\w{1,3}\b', ' ', content)

        # Remove extra spaces
        content = re.sub(r'\s+', ' ', content)

        return content
