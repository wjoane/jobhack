CREATE TABLE `descriptions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `url` TEXT NOT NULL,
  `code` SMALLINT NOT NULL,
  `lang` VARCHAR(2),
  `content` MEDIUMTEXT NOT NULL,
  `label` decimal(4,2),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
