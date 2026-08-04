DROP TABLE IF EXISTS quickpark;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE quickpark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    level TEXT,
    row TEXT,
    landmark TEXT,
    notes TEXT,
    latitude TEXT,
    longitude TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
