"""
CS3810: Principles of Database Systems
Instructor: Thyago Mota
Student(s): Nathan Mead and Mitchell Thompson
Description: A room reservation system
"""

import psycopg2
from psycopg2 import extensions, errors
import configparser as cp
from datetime import datetime

def menu(): 
    print('1. List')
    print('2. Reserve')
    print('3. Delete')
    print('4. Quit')

def db_connect():
    config = cp.RawConfigParser()
    config.read('ConfigFile.properties')
    params = dict(config.items('db'))
    conn = psycopg2.connect(**params)
    conn.autocommit = False 
    with conn.cursor() as cur: 
        cur.execute('''
            PREPARE QueryReservationExists AS 
                SELECT * FROM Reservations 
                WHERE abbr = $1 AND room = $2 AND date = $3 AND period = $4;
        ''')
        cur.execute('''
            PREPARE QueryReservationExistsByCode AS 
                SELECT * FROM Reservations 
                WHERE code = $1;
        ''')
        cur.execute('''
            PREPARE NewReservation AS 
                INSERT INTO Reservations (abbr, room, date, period, "user") VALUES
                ($1, $2, $3, $4, $5);
        ''')
        cur.execute('''
            PREPARE UpdateReservationUser AS 
                UPDATE Reservations SET "user" = $1
                WHERE abbr = $2 AND room = $3 AND date = $4 AND period = $5; 
        ''')
        cur.execute('''
            PREPARE DeleteReservation AS 
                DELETE FROM Reservations WHERE code = $1;
        ''')
        cur.execute('''
            PREPARE NewUser AS 
                INSERT INTO Users (name) VALUES
                ($1);
        ''')
    return conn

# TODO: display all reservations in the system using the information from ReservationsView
def list_op(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM ReservationsView;')
    print("code |    date    | period |  start   |   end    |  room   |     name")
    print("-----+------------+--------+----------+----------+---------+---------------")
    for row in cur.fetchall(): 
        code, date, period, start, end, room, name = row
        print(f"{code:5d} | {date} | {period:6s} | {start} | {end} | {room:7s} | {name}")

# TODO: reserve a room on a specific date and period, also saving the user who's the reservation is for
def reserve_op(conn): 
    name = input('Please enter the name for the booking: ')
    name = name.title()
    sql = "SELECT name FROM Users WHERE name = '" + name + "';"
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) > 0:
        sql = "SELECT \"user\" FROM Users WHERE name = '" + name + "';"
        cur.execute(sql)
        result = cur.fetchall()
        user = result[0][0]
    else: 
        cur.execute("EXECUTE NewUser (%s);", (name,))
        sql = "SELECT \"user\" FROM Users WHERE name = '" + name + "';"
        cur.execute(sql)
        result = cur.fetchall()
        user = result[0][0]
    end = False
    while not end:
        date = input('Please insert the date of the booking (yyyy-mm-dd):')
        if (len(date) != 10):
            print("Invalid entry, please try again")
        else:
            end = True
    end = False
    while not end:
        abbr = input('Which building (AES, JSS)? ')
        if abbr.upper() == "AES":
            end = True
            ended = False
            while not ended:
                room = input('Which room (210, 220)? ')
                if room.isdigit() and (int(room) == 210 or int(room) == 220):
                    ended = True
                else:
                    print("Invalid entry, please try again!")
        elif abbr.upper() == "JSS":
            end = True
            room = 230
        else:
            print('Invalid entry, please try again');
    end = False
    while not end:
        print('Please pick a time slot between the following options:')
        print('(Insert the letter associated with each time slot)')
        print('A: 6:00 - 8:00')
        print('B: 8:00 - 10:00')
        print('C: 10:00 - 12:00')
        print('D: 12:00 - 14:00')
        print('E: 14:00 - 16:00')
        print('F: 16:00 - 18:00')
        print('G: 18:00 - 20:00')
        print('H: 20:00 - 22:00')
        period = input('? ')
        if(period.upper() != "A" and period.upper() != "B" and period.upper() != "C" and period.upper() != "C" and period.upper() != "D" and period.upper() != "E" and period.upper() != "F" and period.upper() != "G" and period.upper() != "H"):
            print("Invalid entry, please try again")
        else:
            end = True
    cur.execute("EXECUTE QueryReservationExists (%s, %s, %s, %s);", (abbr.upper(), room, date, period.upper()))
    result = cur.fetchall()
    if len(result) > 0:
        print("I'm sorry. This room is already booked for that date and time.\n")
    else:
        cur.execute("EXECUTE NewReservation (%s, %s, %s, %s, %s);", (abbr.upper(), room, date, period.upper(), user))
        print('Your booking was successful!\n')
    conn.commit()
    cur.close()


# TODO: delete a reservation given its code
def delete_op(conn):
    reservation_codes = []
    name = input('Please enter the name on the booking: ')
    name = name.title()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ReservationsView WHERE name = '" + name + "';")
    result = cur.fetchall()
    if len(result) > 0:
        cur.execute("SELECT * FROM ReservationsView WHERE name = '" + name + "';")
        print("code |    date    | period |  start   |   end    |  room   |     name")
        print("-----+------------+--------+----------+----------+---------+---------------")
        for row in cur.fetchall(): 
            code, date, period, start, end, room, name = row
            print(f"{code:5d} | {date} | {period:6s} | {start} | {end} | {room:7s} | {name}")
            reservation_codes.append(code)
        end = False
        while not end:
            code = input('? ')
            if int(code) in reservation_codes:
                cur.execute("EXECUTE QueryReservationExistsByCode (%s);", (code,))
                result = cur.fetchall()
                if len(result) > 0:
                    end = True
                    cur.execute("EXECUTE DeleteReservation (%s);", (code,))
                    print("The booking was successfully deleted!\n")
                else: 
                    print('Invalid entry, please try again!')
            else:
                print('Invalid entry, please try again!')

    else:
        print('No bookings were found under ' + name + '.\n')

    

if __name__ == "__main__":
    with db_connect() as conn: 
        op = 0
        while op != 4: 
            menu()
            op = int(input('? '))
            if op == 1: 
                list_op(conn)
            elif op == 2:
                reserve_op(conn)
            elif op == 3:
                delete_op(conn)