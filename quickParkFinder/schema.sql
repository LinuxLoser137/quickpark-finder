DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS quickpark;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE quickpark (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    location TEXT NOT NULL,
    level TEXT,
    row TEXT,
    notes TEXT,
    FOREIGN KEY (user_id) references user (id)
);