DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS bookings;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE client (
    uid INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    pronouns TEXT
);

CREATE TABLE requests (
    rid INTEGER PRIMARY KEY,
    uid INTEGER NOT NULL,
    flash_custom INTEGER NOT NULL DEFAULT 0,
    custom_idea TEXT,
    size TEXT NOT NULL,
    placement TEXT NOT NULL,
    budget TEXT,
    reference TEXT NOT NULL
);

CREATE TABLE bookings (
    bid INTEGER PRIMARY KEY,
    uid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    deposit INTEGER NOT NULL,
    confirmed INTEGER NOT NULL DEFAULT 0,
    length INTEGER NOT NULL,
    date TEXT,
    time TEXT,
    size TEXT NOT NULL,
    placement TEXT NOT NULL,
    budget TEXT,
    token TEXT NOT NULL,
    reference TEXT
);