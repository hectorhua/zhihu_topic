SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `topic`;
CREATE TABLE `topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `topic_id` varchar(100) DEFAULT NULL,
  `topic_name` varchar(100) DEFAULT NULL,
  `topic_url` varchar(200) DEFAULT NULL,
  `follower_count` varchar(10) DEFAULT NULL COMMENT '关注人数',
  `describe` varchar(500) DEFAULT NULL COMMENT '描述',
  `father_topic` varchar(100) DEFAULT NULL COMMENT '父话题',
  `flag` enum('normal','expired','deleted','other') DEFAULT 'normal',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_topic_id` (`topic_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

