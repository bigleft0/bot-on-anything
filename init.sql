CREATE TABLE if not exists tb_admin_user (
	id int NOT NULL,
	user_name varchar(64) NULL,
	code varchar(64) not NULL,
	pwd varchar(64) NULL,
	type int DEFAULT 0,--0:长期用户，1：临时用户
	create_time timestamp,
	CONSTRAINT tb_admin_user PRIMARY KEY (id)
);



