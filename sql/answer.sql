SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `answer`;
CREATE TABLE `answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `answer_id` varchar(20) DEFAULT NULL,
  `answer_url` varchar(200) DEFAULT NULL,
  `question_id` varchar(20) DEFAULT NULL,
  `author_name` varchar(100) DEFAULT NULL,
  `author_domain` varchar(100) DEFAULT NULL,
  `author_type` varchar(20) DEFAULT NULL,
  `author_headline` varchar(300) DEFAULT NULL,
  `author_id` varchar(40) DEFAULT NULL,
  `content` mediumtext,
  `answer_updated_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `answer_create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `voteup_count` int(10) DEFAULT NULL,
  `comment_count` int(10) DEFAULT NULL,
  `flag` enum('normal','crawled','deleted','other') DEFAULT 'normal',
  `crawl_count` int(5) DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_answer_id` (`answer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=935899 DEFAULT CHARSET=utf8;
