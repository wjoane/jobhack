import logging
import mysql.connector


class MysqlUtil:
    def __init__(self, db_config, auto_commit=True):
        logging.info('Connection to database on ' + db_config['host'])
        self.__mydb = mysql.connector.connect(host=db_config['host'],
                                              user=db_config['user'],
                                              password=db_config['password'],
                                              database=db_config['database'])
        self.__auto_commit = auto_commit

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
            sql = "INSERT INTO `descriptions` (`url`, `code`, `content`) VALUES (%s, %s, %s);"
            val = (page['url'], page['code'], page['content'])
            try:
                mycursor.execute(sql, val)
                if self.__auto_commit:
                    self.__mydb.commit()
            except Exception as e:
                logging.error("Unable to commit SQL commands")
                logging.error(str(e))

        mycursor.close()
