drop database if exists lianjia;

create database lianjia;

use lianjia;

grant select, insert, update, delete on lianjia.* to 'lianjia'@'localhost' identified by 'lianjia';

create table xiaoqu(
  `name` varchar(45) NOT NULL,
  `url` varchar(100) NOT NULL,
  `region` varchar(45) NOT NULL,
  `regions` varchar(200) NOT NULL,
  `year` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

create table chengjiao(
  `href` varchar(100) NOT NULL,
  `name` varchar(45) NOT NULL,
  `style` varchar(45) NOT NULL,
  `area` varchar(45) NOT NULL,
  `orientation` varchar(10) NOT NULL,
  `floor` varchar(45) NOT NULL,
  `year` varchar(45) NOT NULL,
  `sign_time` varchar(45) NOT NULL,
  `unit_price` varchar(45) NOT NULL,
  `total_price` varchar(45) NOT NULL,
  `fangchan_class` varchar(45) NOT NULL,
  `school` varchar(45) NOT NULL,
  `subway` varchar(45) NOT NULL,
  `distribution` varchar(45) NOT NULL,
  `elevator` varchar(45) NOT NULL,
  `listing` varchar(45) NOT NULL,
  PRIMARY KEY (`href`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;