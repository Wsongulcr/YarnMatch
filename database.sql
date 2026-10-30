CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE yarn_stash (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    brand VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    material VARCHAR(100),
    weight_category VARCHAR(50) NOT NULL,
    color_hex VARCHAR(7),
    remaining_grams INT NOT NULL,
    remaining_meters INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE saved_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ravelry_pattern_id INT NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    status ENUM('a_faire', 'en_cours', 'termine') DEFAULT 'a_faire',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);