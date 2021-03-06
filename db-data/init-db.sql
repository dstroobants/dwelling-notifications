CREATE DATABASE IF NOT EXISTS dwellings;
USE dwellings;
CREATE TABLE IF NOT EXISTS links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    daft_id VARCHAR(255),
    myhome_id VARCHAR(255),
    url TEXT NOT NULL,
    title TEXT,
    notified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)  ENGINE=INNODB;
