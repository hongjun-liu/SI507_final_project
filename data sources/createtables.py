import sqlite3
import csv

conn = sqlite3.connect("parksandtrails.sqlite")
cur = conn.cursor()

drop_parks='''
       DROP TABLE IF EXISTS "parks"; 
'''

create_parks='''
    CREATE TABLE IF NOT EXISTS "parks"(
        "Id"   INTEGER PRIMARY KEY,
        "ParkCode"   TEXT NOT NULL, 
        "ParkName"   TEXT NOT NULL, 
        "State"       TEXT NOT NULL, 
        "zipcode"     REAL NOT NULL, 
        "phone"       REAL NOT NULL
       );
'''

cur.execute(drop_parks)
cur.execute(create_parks)

with open("parks.csv",'r') as parks:
    diction=csv.DictReader(parks)
    database=[(i["Id"],i['parkcode'], i['park'].rstrip(), i['state'], i['zipcode'], i['phone']) for i in diction]

cur.executemany("INSERT INTO parks VALUES (?,?, ?, ?, ?, ?);", database)



drop_trails='''
       DROP TABLE IF EXISTS "trails"; 
'''

create_trails='''
       CREATE TABLE IF NOT EXISTS "trails"(
        "trail_id"  REAL PRIMARY KEY,
        "ParkName" TEXT NOT NULL, 
        "elevation_gain" REAL NOT NULL, 
        "difficulty_rating" REAL NOT NULL, 
        "popularity" REAL NOT NULL, 
        "leng" REAL NOT NULL, 
        "num_reviews" REAL NOT NULL
       );
'''

cur.execute(drop_trails)
cur.execute(create_trails)

with open("Trails.csv",'r') as trails:
    diction2=csv.DictReader(trails)
    database2=[(i["trail_id"],i['park_name'].rstrip(), i['elevation_gain'], i['difficulty_rating'], i['popularity'], i['length'], i['num_reviews']) for i in diction2]

cur.executemany("INSERT INTO trails VALUES (?, ?, ?, ?, ?, ?,?);", database2)

conn.commit()
conn.close()




