SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `question`;
CREATE TABLE `question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` varchar(100) DEFAULT NULL,
  `question_url` varchar(200) DEFAULT NULL,
  `topic_id` varchar(100) DEFAULT NULL,
  `question_title` varchar(200) DEFAULT NULL,
  `question_text` mediumtext,
  `follower_count` varchar(10) DEFAULT NULL COMMENT '关注人数',
  `scan_count` varchar(10) DEFAULT NULL COMMENT '浏览人数',
  `answer_count` varchar(10) DEFAULT NULL COMMENT '回答数',
  `question_tag` varchar(500) DEFAULT NULL COMMENT '问题标签，以|分隔',
  `flag` enum('normal','expired','deleted','other') DEFAULT 'normal',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_question_topic_id` (`question_id`, `topic_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

