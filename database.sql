CREATE DATABASE ecommerce;

USE ecommerce;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'User'
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    status VARCHAR(30) DEFAULT 'Ordered',

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO users(username,password,role)
VALUES
('admin','admin123','Admin'),
('user','user123','User');

INSERT INTO products(name,price,quantity)
VALUES
('Laptop',55000,10),
('Smartphone',25000,20),
('Headphones',2000,30),
('Keyboard',1500,15),
('Mouse',800,25);
