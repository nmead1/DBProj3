-- CS3810: Principles of Database Systems
-- Instructor: Thyago Mota
-- Student(s): 
-- Description: booking database

DROP DATABASE booking;

CREATE DATABASE booking;

\c booking

CREATE TABLE Users (
    "user" SERIAL PRIMARY KEY, 
    name VARCHAR(50) NOT NULL
);

INSERT INTO Users (name) VALUES 
    ('Sam Mai Tai'), ('Morbid Mojito'), ('James Brandy');

CREATE TABLE Buildings (
    abbr VARCHAR(5) PRIMARY KEY, 
    title VARCHAR(50)
);

INSERT INTO Buildings VALUES 
    ('AES', 'Aerospace and Engineering Science'), 
    ('JSS', 'Jordan Student Success');

CREATE TABLE Rooms (
    abbr VARCHAR(5) NOT NULL, 
    room INT NOT NULL, 
    PRIMARY KEY (abbr, room), 
    FOREIGN KEY (abbr) REFERENCES Buildings (abbr)
);

INSERT INTO Rooms VALUES
    ('AES', 210), ('AES', 220), ('JSS', 230);

CREATE TABLE Periods (
    period CHAR(1) PRIMARY KEY, 
    start TIME NOT NULL, 
    "end" TIME NOT NULL
);

INSERT INTO Periods VALUES 
    ('A', '06:00:00', '08:00:00'), 
    ('B', '08:00:00', '10:00:00'),
    ('C', '10:00:00', '12:00:00'),
    ('D', '12:00:00', '14:00:00'),
    ('E', '14:00:00', '16:00:00'),
    ('F', '16:00:00', '18:00:00'),
    ('G', '18:00:00', '20:00:00'),
    ('H', '20:00:00', '22:00:00');

CREATE TABLE Reservations (
    code SERIAL PRIMARY KEY, 
    abbr VARCHAR(5), 
    room INT, 
    date DATE NOT NULL, 
    period CHAR(1), 
    "user" INT, 
    FOREIGN KEY (abbr, room) REFERENCES Rooms (abbr, room), 
    FOREIGN KEY (period) REFERENCES Periods (period),
    FOREIGN KEY ("user") REFERENCES Users ("user")
);

INSERT INTO Reservations (abbr, room, date, period, "user") VALUES
    ('AES', 210, '2023-05-15', 'C', 1), 
    ('AES', 210, '2023-06-12', 'D', 1), 
    ('AES', 220, '2023-06-23', 'E', 2), 
    ('JSS', 230, '2023-06-23', 'F', 3);

CREATE USER booking PASSWORD '135791';
GRANT ALL ON TABLE Users TO booking;
GRANT ALL ON TABLE Buildings TO booking;
GRANT ALL ON TABLE Rooms TO booking;
GRANT ALL ON TABLE Periods TO booking;
GRANT ALL ON TABLE Reservations TO booking;
GRANT ALL ON SEQUENCE reservations_code_seq TO booking;
GRANT ALL ON SEQUENCE users_user_seq TO booking;

-- TODO: create a view called ReservationsView to retrieve all reservation information in chronological order similar to the one below
--  code |    date    | period |  start   |   end    |  room   |     name      
-- ------+------------+--------+----------+----------+---------+---------------
--     4 | 2023-06-23 | F      | 16:00:00 | 18:00:00 | JSS-230 | James Brandy
--     3 | 2023-06-23 | E      | 14:00:00 | 16:00:00 | AES-220 | Morbid Mojito
--     2 | 2023-06-12 | D      | 12:00:00 | 14:00:00 | AES-210 | Sam Mai Tai
--     1 | 2023-05-15 | C      | 10:00:00 | 12:00:00 | AES-210 | Sam Mai Tai

-- once your view is created and working, run the following line
GRANT ALL ON TABLE ReservationsView TO booking;