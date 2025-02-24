import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="library"
)

cursor = db.cursor()


db.commit()
print("Database connected successfully!")