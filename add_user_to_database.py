import smtplib
import sys
from werkzeug.security import check_password_hash, generate_password_hash
import string
from random import *
import os
import psycopg2


admin_password_hash = "pbkdf2:sha256:50000$eOSx6nau$e46af3e22e0a76f4a7f6055c39dd9e619d2a21d8bc9414ab929446d343ae6782"
admin_username_hash = "pbkdf2:sha256:50000$WuMSeblg$75ba6597b142ccf3b47a218b48f4df64ca5e17cc8b9ccaae2389f9f1f25a610a"




class Admin:

    generated_password = ""
    DATABASE_URL = os.environ['DATABASE_URL']



    def generate_random_password(self):
        characters = string.ascii_letters + string.digits
        password =  "".join(choice(characters) for x in range(randint(6, 7)))
        return password



    def write_db(self,user_type,student_no_username, name, sname):
        connection = psycopg2.connect(self.DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:

            password_hash = generate_password_hash(self.generated_password)

            if user_type == "student":
                cursor.execute("INSERT INTO Student (student_no,password,name,sname)\
                VALUES (%s,%s,%s,%s)",( student_no_username, password_hash, name, sname ))


            else:
                cursor.execute("INSERT INTO Academician (username,password,name,sname)\
                VALUES (%s,%s,%s,%s)",( student_no_username, password_hash, name, sname ))


            connection.commit()


        finally:
            connection.close()
