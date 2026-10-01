-- Capstone Project 2
-- SQL Capstone Project - 2
-- Practice: LIKE, DISTINCT, WHERE filtering, and ORDER BY sorting.
-- Run this whole script in SQLite, MySQL, or PostgreSQL.
-- SQLite:  sqlite3 capstone.db < capstone.sql

DROP TABLE IF EXISTS library_books;

CREATE TABLE library_books (
    book_id     INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    genre       TEXT NOT NULL,
    language    TEXT NOT NULL,
    year_pub    INTEGER NOT NULL,
    copies      INTEGER NOT NULL,
    available   INTEGER NOT NULL
);

INSERT INTO library_books (book_id, title, author, genre, language, year_pub, copies, available) VALUES
(1,  'The Silent Library',      'Amina Farouk',   'Mystery',    'English', 2018, 6, 4),
(2,  'Blue River Map',          'Leo Martins',    'Adventure',  'English', 2015, 4, 1),
(3,  'Like the Wind',           'Nora Blake',     'Poetry',     'English', 2020, 3, 3),
(4,  'History of Clocks',       'Samir Haddad',   'History',    'English', 2011, 5, 2),
(5,  'Clockwork Garden',        'Samir Haddad',   'Fantasy',    'English', 2019, 7, 5),
(6,  'El mapa del rio',         'Leo Martins',    'Adventure',  'Spanish', 2016, 2, 2),
(7,  'Little Lights',           'Nora Blake',     'Poetry',     'English', 2022, 8, 6),
(8,  'Science Lab Notes',       'Priya Shah',     'Science',    'English', 2014, 10, 0),
(9,  'Lab Stories for Kids',    'Priya Shah',     'Science',    'English', 2021, 9, 7),
(10, 'A Likely Story',          'Jonah Reed',     'Mystery',    'English', 2009, 3, 1),
(11, 'Desert Atlas',            'Amina Farouk',   'History',    'Arabic',  2017, 4, 4),
(12, 'River Atlas',             'Leo Martins',    'Adventure',  'English', 2013, 5, 3),
(13, 'Unlike Any Other',       'Jonah Reed',     'Mystery',    'English', 2023, 6, 6),
(14, 'Garden of Time',         'Samir Haddad',   'History',    'English', 2008, 2, 0),
(15, 'Wind and Stone',          'Nora Blake',     'Poetry',     'French',  2012, 3, 2);

-- 1) LIKE: titles that contain the letters "like" anywhere
SELECT book_id, title, author
FROM library_books
WHERE title LIKE '%like%'
ORDER BY title ASC;

-- 2) LIKE with a single-character wildcard: titles starting with any one letter, then "l"
SELECT title, author
FROM library_books
WHERE title LIKE '_l%'
ORDER BY title;

-- 3) LIKE prefix: authors whose name starts with S
SELECT title, author, genre
FROM library_books
WHERE author LIKE 'S%'
ORDER BY author, title;

-- 4) DISTINCT genres only
SELECT DISTINCT genre
FROM library_books
ORDER BY genre ASC;

-- 5) DISTINCT author + genre pairs (same author can write more than one genre)
SELECT DISTINCT author, genre
FROM library_books
ORDER BY author ASC, genre ASC;

-- 6) Filter + sort: English books that still have copies available, cheapest-year first
SELECT title, author, year_pub, available
FROM library_books
WHERE language = 'English'
  AND available > 0
ORDER BY year_pub ASC, title ASC;

-- 7) Mixed: DISTINCT genres of books whose title contains "a",
--    published after 2010, sorted Z to A
SELECT DISTINCT genre
FROM library_books
WHERE title LIKE '%a%'
  AND year_pub > 2010
ORDER BY genre DESC;

-- 8) Mixed: unique authors who wrote Adventure or Mystery,
--    title contains "r" or "R", at least 2 copies available
SELECT DISTINCT author
FROM library_books
WHERE (genre = 'Adventure' OR genre = 'Mystery')
  AND (title LIKE '%r%' OR title LIKE '%R%')
  AND available >= 2
ORDER BY author ASC;

-- 9) Filter by pattern and sort by stock
SELECT title, genre, copies, available
FROM library_books
WHERE title LIKE '%Atlas%'
   OR title LIKE '%Map%'
ORDER BY available DESC, title ASC;

-- 10) Challenge query: one row per author, only authors with a title like '%o%',
--     showing how many matching books, sorted by that count then name
SELECT author,
       COUNT(DISTINCT title) AS matching_titles
FROM library_books
WHERE title LIKE '%o%'
GROUP BY author
ORDER BY matching_titles DESC, author ASC;
