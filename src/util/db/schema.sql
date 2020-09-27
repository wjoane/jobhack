CREATE TABLE `descriptions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `url` TEXT NOT NULL,
  `code` SMALLINT NOT NULL,
  `lang` VARCHAR(2) NOT NULL DEFAULT 'en',
  `content` MEDIUMTEXT NOT NULL,
  `label` decimal(5,4) NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
