import os
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']


class Project:
    def __init__(self, project_id, project_name, project_type):
        self.project_id = project_id
        self.project_name = project_name
        self.project_type = project_type



class Appointment:
    def __init__(self, appointment_id, appointment_name, appointment_date):
        self.appointment_id = appointment_id
        self.appointment_name = appointment_name
        self.appointment_date = appointment_date





class Student():
    def __init__(self, student_no, password, name, sname):
        #Class icerisinde sadece degerleri dinamik olarak degismeyen degerlerin (ogrenci no, isim & soyisim gibi) uye alanlari bulunmaktadir.
        #Sebebi asagidaki notta aciklanmistir.
        self.student_no = student_no
        self.password = password
        self.name = name
        self.sname = sname


    #NOT: project, grade gibi alanlar icin class icerisinde uye alani kullanilmamistir. Cunku web tabanli uygulamada
    #kullanicilarin manipulasyonu sonucu bu degerler dinamik olarak degisebilir.


    def get_project(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT Student.project_id, project_name, project_type FROM Student,Project WHERE student_no=%s AND Student.project_id=Project.project_id', (self.student_no,)).fetchone()
            data=cursor.fetchone()
            if data:
                return Project(data[0], data[1], data[2])
        finally:
            connection.close()



    #Gets student's project grade.
    def get_grade(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT grade FROM Student WHERE student_no=%s', (self.student_no,))
            data = cursor.fetchone()
            if data:
                return data[0]
        finally:
            connection.close()



    #Gets academician username
    def get_academician(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute(
            'SELECT Academician.username FROM Student,Project,Academician WHERE student_no=%s AND \
            Student.project_id=Project.project_id AND \
            Project.username=Academician.username', (self.student_no,))

            data = cursor.fetchone()

            if data:

                return data[0]
        finally:
            connection.close()




    #NOT: set_academician metodu mantiksiz olacagi icin tanimlanmamistir. Cunku ogrencilerin akademisyenleri zaten set_project araciligi ile
    #dolayli olarak set ediliyor.



    #Gets students's appointment's id with the academician
    def get_appointment(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT Student.appointment_id, Appointment.appointment_name, Appointment.appointment_date \
            FROM Student,Appointment \
            WHERE student_no=%s AND Student.appointment_id=Appointment.appointment_id', (self.student_no,))

            data = cursor.fetchone()

            if data:
                return Appointment(data[0], data[1], data[2])
        finally:
            connection.close()



    #Sonraki gelistirmelere birakilmistir
    def set_appointment(self):
        pass




    #NOT: Randevu ekleme ve duzenleme gibi metotlar sonraki gelistirmelere birakilmistir.



    #Bu metot objenin uye alanlarini sinif icerisinde set edip, objeyi return etmektedir.
    @classmethod
    def find_by_student_no(cls, student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT student_no,password,name,sname FROM Student WHERE student_no=%s', (student_no,))
            data = cursor.fetchone()
            if data:
                #cls mevcut sinifin contructor ini temsil etmektedir
                instance = cls(data[0], data[1], data[2], data[3])
                return instance
        finally:
            connection.close()





class Academician():
    def __init__(self, username, password, name, sname):
        self.username = username
        self.password = password
        self.name = name
        self.sname = sname


    #Gets all projects that belong to academician
    def get_projects(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT project_id,project_name,project_type \
            FROM Academician,Project \
            WHERE Academician.username=%s AND \
            Project.username=Academician.username', (self.username,))

            data = cursor.fetchall()

            if data:
                project_list = []

                for query_row in data:
                    project_list.append( Project(query_row[0], query_row[1], query_row[2]) )

                return project_list
        finally:
            connection.close()




    #Gets Academician's students' numbers.
    def get_students(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute(
            'SELECT student_no,Student.password,Student.name,Student.sname FROM Student,Project,Academician WHERE Academician.username=%s AND \
            Academician.username=Project.username AND \
            Student.project_id=Project.project_id', (self.username,))

            data = cursor.fetchall()

            if data:
                student_list = []

                for query_row in data:
                    student_list.append( Student(query_row[0], query_row[1], query_row[2], query_row[3]) )

                return student_list

        finally:
            connection.close()


    #Gets academician's appointments
    def get_appointments(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT Appointment.appointment_id,appointment_name,appointment_date \
             FROM Academician,Appointment \
             WHERE Academician.username=%s AND \
             Appointment.username=Academician.username', (self.username,))

            data = cursor.fetchall()

            if data:
                appointment_list = []

                for query_row in data:
                    appointment_list.append( Appointment(query_row[0], query_row[1], query_row[2]) )

                return appointment_list
        finally:
            connection.close()



    #Sets project grade of student with given student_no
    def set_grade(self, student_no, grade):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            #IN statement, guvenligi artirmak icin eklenmistir. Hocanin sadece kendine bagli bir ogrenciye not girisi yaptigindan emin olmak icin...
            cursor.execute(
            'UPDATE Student \
            SET grade=%s \
            WHERE student_no=%s AND \
            project_id IN ( \
            SELECT project_id \
            FROM Project,Academician \
            WHERE Project.username=Academician.username AND Academician.username=%s)', (grade, student_no, self.username))

            return True

        finally:
            connection.commit()
            connection.close()



    #Sonraki gelistirmelere birakilmistir
    def set_project(self, project):
        pass




    #Bu metot objenin uye alanlarini sinif icerisinde set edip, objeyi return etmektedir.
    @classmethod
    def find_by_username(cls, username):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT username,password,name,sname FROM Academician WHERE username=%s', (username,))
            data = cursor.fetchone()
            if data:
                instance = cls(data[0], data[1], data[2], data[3])

                return instance
        finally:
            connection.close()
