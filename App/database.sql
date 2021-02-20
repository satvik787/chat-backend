CREATE TABLE users(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(30) NOT NULL UNIQUE,
    image_path VARCHAR(255),
    msg_count INT,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password VARCHAR(30) NOT NULL 
);
CREATE TABLE channels(
    channel_id int PRIMARY KEY AUTO_INCREMENT NOT NULL,
    user_one_id INT NOT NULL,
    user_two_id INT NOT NULL,
    chain_one DECIMAL(5,4) default 0,
    chain_two DECIMAL(5,4) default 0,
    FOREIGN KEY (user_one_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_two_id) REFERENCES users (user_id) ON DELETE CASCADE
);
CREATE TABLE messages(
    msg_id int PRIMARY KEY  NOT NULL,
    channel_id INT NOT NUll,
    user_id INT NOT NULL,
    msg VARCHAR(150) NOT NULL,
    chain_val DECIMAL(5,4) NOT NULL,
    sent_at VARCHAR(50) NOT NULL,
    FOREIGN KEY (channel_id) REFERENCES channels (channel_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);
