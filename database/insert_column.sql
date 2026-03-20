ALTER TABLE games
add column release_date DATE;

ALTER TABLE users
MODIFY COLUMN email VARCHAR(255) UNIQUE,
MODIFY COLUMN password_hash VARCHAR(255);