create database if not exists api_testing_db;
use api_testing_db;

create table if not exists expected_products (
    id int primary key,
    expected_title varchar(255) not null,
    expected_price decimal(10,2) not null
);

insert into expected_products (id, expected_title, expected_price) values (1, 'Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops',109.95)
on duplicate key update
    expected_title = values(expected_title),
    expected_price = values(expected_price);