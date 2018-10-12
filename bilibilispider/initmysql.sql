drop database if exists bilibili;

create database bilibili;

use bilibili;

grant select, insert, update, delete on bilibili.* to 'bilibili'@'localhost' identified by 'bilibili';

create table bilibili_user_info (
 `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `mid` int(20) unsigned NOT NULL,
  `name` varchar(45) NOT NULL,
  `sex` varchar(45) NOT NULL,
  `rank` varchar(45) NOT NULL,
  `face` varchar(200) NOT NULL,
  `regtime` varchar(45) NOT NULL,
  `spacesta` varchar(45) NOT NULL,
  `birthday` varchar(45) NOT NULL,
  `sign` varchar(300) NOT NULL,
  `level` varchar(45) NOT NULL,
  `OfficialVerifyType` varchar(45) NOT NULL,
  `OfficialVerifyDesc` varchar(100) NOT NULL,
  `vipType` varchar(45) NOT NULL,
  `vipStatus` varchar(45) NOT NULL,
  `toutu` varchar(200) NOT NULL,
  `toutuId` int(20) unsigned NOT NULL,
  `coins` int(20) unsigned NOT NULL,
  `following` int(20) unsigned NOT NULL,
  `fans` int(20) unsigned NOT NULL,
  `archiveview` int(20) unsigned NOT NULL,
  `article` int(20) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table url_fail (
  `url` varchar(45)  NOT NULL,
  `status` varchar(200)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
