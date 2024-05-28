CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birthdate DATE NOT NULL,
    country_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
    CONSTRAINT player UNIQUE (first_name, last_name)
);

CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    country_name TEXT NOT NULL UNIQUE
);

CREATE TABLE tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    tournament_name TEXT NOT NULL UNIQUE
);

CREATE TABLE surfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    surface_name TEXT NOT NULL UNIQUE
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    tournament_id INTEGER NOT NULL,
    a_year YEAR NOT NULL,
    surface_id INTEGER NOT NULL,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    FOREIGN KEY (surface_id) REFERENCES surfaces(id),
    CONSTRAINT events UNIQUE (tournament_id, a_year)
);

CREATE TABLE rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    round_name TEXT NOT NULL UNIQUE
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    event_id INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    loser_id INTEGER NOT NULL,
    round_id INTEGER NOT NULL,
    score TEXT NOT NULL,
    a_date DATE NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (round_id) REFERENCES rounds(id),
    CONSTRAINT matches UNIQUE (event_id, winner_id, loser_id, round_id)
);

CREATE TABLE points (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    a_date DATE NOT NULL,
    points INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (match_id) REFERENCES matches(id)
);
