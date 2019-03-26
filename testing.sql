CREATE DATABASE /*!32312 IF NOT EXISTS*/`clm` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `clm`;

CREATE TABLE `food` (
  `foodname` varchar(50) NOT NULL,
  `price` float(10) NOT NULL,
  `type` varchar(50) NOT NULL,
  PRIMARY KEY (`foodname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

insert  into `food`(`foodname`,`price`, `type`) values 
('Pizza', 5.00, 'pizza'),
('Waffles', 4.00, 'grill'),
('Grapes', 4.00, 'packaged'),
('Fries', 2.30, 'grill');
