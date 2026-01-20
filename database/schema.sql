-- Disable checks and clear anything that partially exists
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS user_library, user_sessions, games, users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Users (No automatic timestamp)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at DATETIME,
    is_active TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 2. Games
CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(50),
    price DECIMAL(6,2)
) ENGINE=InnoDB;

-- 3. Sessions (No automatic timestamp)
CREATE TABLE user_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    created_at DATETIME,
    expires_at DATETIME,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. User Library
CREATE TABLE user_library (
    library_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    platform VARCHAR(50),
    CONSTRAINT fk_lib_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_lib_game FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE
) ENGINE=InnoDB;