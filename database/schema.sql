DROP TABLE IF EXISTS user_library;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS oauth_accounts;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    created_at DATETIME,
    is_active TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(50),
    price DECIMAL(6,2),
    tags VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE user_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    created_at DATETIME,
    expires_at DATETIME,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE user_library (
    library_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    platform VARCHAR(50),
    CONSTRAINT fk_lib_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_lib_game FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE oauth_accounts (
    oauth_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider ENUM('google', 'steam', 'epic') NOT NULL,
    provider_account_id VARCHAR(255) NOT NULL,
    access_token VARCHAR(500),
    token_expiry DATETIME,
    linked_at DATETIME,
    CONSTRAINT fk_oauth_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT uq_provider_account UNIQUE (provider, provider_account_id)
) ENGINE=InnoDB;