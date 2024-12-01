DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS requests;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE client (
    uid INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT
);

CREATE TABLE requests (
    rid INTEGER PRIMARY KEY,
    uid INTEGER NOT NULL,
    flash_custom INTEGER NOT NULL DEFAULT 0,
    size REAL NOT NULL,
    placement TEXT NOT NULL,
    reference BLOB NOT NULL
);

