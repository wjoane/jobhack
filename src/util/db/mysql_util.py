import logging

import mysql.connector


class MysqlUtil:
    def __init__(self, db_config, auto_commit=True):
        logging.info('Connection to database on ' + db_config['host'])
        try:
            self.__mydb = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'])
            self.__auto_commit = auto_commit
        except Exception as e:
            logging.error("Unable connect to mySQL Database on host: " +
                          db_config['host'])
            logging.error(str(e))

    def __len__(self):
        logging.info('Loading data from database...')
        mycursor = self.__mydb.cursor(dictionary=True)
        try:
            sql = "SELECT COUNT(*) AS size FROM `descriptions`;"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            return row['size']
        except Exception as e:
            logging.error("Unable to execute SELECT SQL commands")
            logging.error(str(e))
            return 0
        finally:
            mycursor.close()

    def save(self, content, truncate=False):
        mycursor = self.__mydb.cursor()

        if truncate:
            try:
                sql = "TRUNCATE TABLE `descriptions`;"
                mycursor.execute(sql)
            except Exception as e:
                logging.error("Unable to commit SQL commands")
                logging.error(str(e))

        for page in content:
            logging.debug(
                'Inserting description row: ' + page['url'])
            sql = "INSERT INTO `descriptions` (`url`, `code`, `content`) " \
                  "VALUES (%s, %s, %s);"
            val = (page['url'], page['code'], page['content'])
            try:
                mycursor.execute(sql, val)
                if self.__auto_commit:
                    self.__mydb.commit()
            except Exception as e:
                logging.error("Unable to commit INSERT SQL commands")
                logging.error(str(e))

        mycursor.close()

    @property
    def load(self):
        logging.info('Loading data from database...')
        mycursor = self.__mydb.cursor(dictionary=True, buffered=True)
        try:
            sql = "SELECT * FROM `descriptions` ORDER BY `label`;"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            while row:
                yield {k: (v.decode('utf-8') if isinstance(v, bytes) else v)
                       for k, v in row.items()}
                row = mycursor.fetchone()
        except Exception as e:
            logging.error("Unable to execute SELECT SQL commands")
            logging.error(str(e))
        finally:
            mycursor.close()

    def update_labels(self, content):
        mycursor = self.__mydb.cursor()

        for page in content:
            logging.debug(
                'Updating description label: ' + page['url'])
            sql = "UPDATE `descriptions` SET `label` = %s WHERE `url` = %s;"
            val = (page['label'], page['url'])
            try:
                mycursor.execute(sql, val)
                if self.__auto_commit:
                    self.__mydb.commit()
            except Exception as e:
                logging.error("Unable to commit UPDATE SQL commands")
                logging.error(str(e))

        mycursor.close()

    def update_by_url(self, content):
        mycursor = self.__mydb.cursor()

        for page in content:
            logging.debug(
                'Updating description content: ' + page['url'])
            sql = "UPDATE `descriptions` SET `code` = %s, `content` = %s " \
                  "WHERE `url` = %s;"
            val = (page['code'], page['content'], page['url'])
            try:
                mycursor.execute(sql, val)
                if self.__auto_commit:
                    self.__mydb.commit()
            except Exception as e:
                logging.error("Unable to commit UPDATE SQL commands")
                logging.error(str(e))

        mycursor.close()
