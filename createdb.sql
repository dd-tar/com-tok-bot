create table community_chat(
       id integer primary key,
       gt varchar(42)
);

create table approve(
       user_address varchar(255) primary key,
       id varchar(42)
       chat_id varchar(255)
);

