import os
import psycopg2
from psycopg2 import sql


DATABASE_URL = os.environ['DATABASE_URL']


class Project:
    def __init__(self, project_id, project_name, project_type,form2_status,council_decision):
        self.project_id = project_id
        self.project_name = project_name
        self.project_type = project_type
        self.form2_status = form2_status
        self.council_decision = council_decision





    @classmethod
    def get_academician_proposals(cls):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT project_id, project_name, project_type, username FROM Project WHERE proposal_type=%s AND \
            capacity IS NOT NULL', ("academician",))
            data = cursor.fetchall()
            if data:
                return data

            else:
                return None
        finally:
            connection.close()



    @classmethod
    def check_project_capacity(cls, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT fullness,capacity FROM Project WHERE project_id=%s', (project_id,))
            data = cursor.fetchone()

            if data[1]-data[0] > 0:
                return False

            return True

        finally:
            connection.close()




class Appointment:
    def __init__(self, appointment_id, appointment_name, appointment_date):
        self.appointment_id = appointment_id
        self.appointment_name = appointment_name
        self.appointment_date = appointment_date





class Student():
    def __init__(self, student_no, password, name, sname,continuation):
        #Class icerisinde sadece degerleri dinamik olarak degismeyen degerlerin (ogrenci no, isim & soyisim gibi) uye alanlari bulunmaktadir.
        #Sebebi asagidaki notta aciklanmistir.
        self.student_no = student_no
        self.password = password
        self.name = name
        self.sname = sname
        self.continuation = continuation


    #NOT: project, grade gibi alanlar icin class icerisinde uye alani kullanilmamistir. Cunku web tabanli uygulamada
    #kullanicilarin manipulasyonu sonucu bu degerler dinamik olarak degisebilir.


    def get_project(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT Student.project_id, project_name, project_type, form2_status,form2_council_decision FROM Student,Project WHERE student_no=%s AND Student.project_id=Project.project_id', (self.student_no,))
            data=cursor.fetchone()
            if data:
                return Project(data[0], data[1], data[2], data[3], data[4])

            else:
                return None
        finally:
            connection.close()


    #Başvurulan proje bilgileri döndürülür
    def get_applied_project(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT apply_project_id, apply_project_status,project_id FROM \
            Student WHERE student_no=%s', (self.student_no,))
            data=cursor.fetchone()

            #Proje başvurusu varsa
            if data[0]:
                which_project = data[0]

                #Onaylanmis proje varsa guncel adiyla gostermek icin
                if data[2]:
                    which_project = data[2]

                cursor.execute('SELECT project_name, proposal_type, project_type, username FROM \
                Project WHERE project_id=%s', (which_project,))

                data_project = cursor.fetchone()
                data_project = data_project + (data[1],)

                return data_project

            else:
                return None
        finally:
            connection.close()



    #Proje başvurusu silinir
    def delete_project_apply(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            #Proje bilgisi cekiliyor
            cursor.execute('SELECT project_id \
            FROM Student \
            WHERE student_no=%s',(self.student_no,))

            data = cursor.fetchone()

            #Proje basvurusu onaylanmamis ise
            if not data[0]:
                #Proje akademisyen onerisinden ve basvuru durumu pending ise basvuru sayisi guncellenir
                cursor.execute('UPDATE Project \
                SET app_count=app_count-1 WHERE \
                proposal_type=%s AND project_id IN(SELECT apply_project_id FROM Student WHERE student_no=%s AND apply_project_status=%s) ',("academician",self.student_no,"pending"))

                #Projeyi öğrenci önerdiyse Proje tablosundaki öğrenci önerisi de silinir
                cursor.execute('DELETE FROM Project \
                WHERE proposal_type=%s AND \
                project_id IN(SELECT apply_project_id FROM Student WHERE student_no=%s) ',("student",self.student_no))


                cursor.execute('UPDATE Student \
                SET apply_project_id=%s, apply_project_status=%s \
                WHERE student_no=%s OR friend_student_no=%s',(None, None, self.student_no, self.student_no))




        finally:
            connection.commit()
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
            'SELECT Project.username FROM Student,Project WHERE student_no=%s AND \
            (Student.project_id=Project.project_id OR Student.apply_project_id=Project.project_id) ', (self.student_no,))

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



    def add_form2(self, form2_blob_data):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            form2_status = "academician_pending"
            cursor.execute('UPDATE Project \
            SET form2=%s, form2_status=%s \
            WHERE project_id IN(\
            SELECT project_id FROM Student WHERE student_no=%s)',(psycopg2.Binary(form2_blob_data), form2_status, self.student_no))

            return True

            """
            curs.execute("insert into blobs (file) values (%s)",
            (psycopg2.Binary(mypic),))
            """

        finally:
            connection.commit()
            connection.close()



    def add_report(self, report_type, report_blob_data):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        exist_word = report_type + "_exist"

        try:

            cursor.execute(
            sql.SQL("UPDATE Project SET {}=%s,{}=%s WHERE project_id IN(SELECT project_id FROM Student WHERE student_no=%s)").format(
            *map(sql.Identifier, (report_type, exist_word))), (psycopg2.Binary(report_blob_data),"true",self.student_no))

            return True

        finally:
            connection.commit()
            connection.close()



    #Gets report with given report type
    def get_report(self, report_type):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute(
            sql.SQL("SELECT {} FROM Project,Student WHERE Student.project_id=Project.project_id AND student_no=%s").format(
            sql.Identifier(report_type)), (self.student_no,))

            data = cursor.fetchone()

            if data:

                return data[0]
        finally:
            connection.close()



    #NOT: Randevu ekleme ve duzenleme gibi metotlar sonraki gelistirmelere birakilmistir.


    #Öğrencinin akademisyen önerisinden olan projeye başvurması için
    def apply_academician_project(self, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            status = "pending"
            cursor.execute('UPDATE Student \
            SET apply_project_id=%s, apply_project_status=%s \
            WHERE (student_no=%s OR friend_student_no=%s)',(project_id, status, self.student_no, self.student_no))

            return True

            """
            curs.execute("insert into blobs (file) values (%s)",
            (psycopg2.Binary(mypic),))
            """

        finally:
            connection.commit()
            connection.close()




    #Öğrencinin kendi proje önerisiyle başvuru yapması
    def apply_student_project(self, project_name, project_type, academician_username):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            status = "pending"
            #Akademisyen gercek mi?
            cursor.execute('SELECT username, name\
            FROM Academician WHERE username=%s', (academician_username,) )

            academician = cursor.fetchone()

            if academician:

                #Project tablosuna öğrenci önerisi ekleniyor
                cursor.execute('INSERT INTO Project(project_name, project_type, username, proposal_type)\
                VALUES (%s,%s,%s,%s) RETURNING project_id;', (project_name, project_type, academician_username, "student") )

                project_id = cursor.fetchone()[0]

                #Öğrenci tablosunda önerilen projenin idsi alınıp set ediliyor
                cursor.execute('UPDATE Student \
                SET apply_project_id=%s, apply_project_status=%s \
                WHERE student_no=%s OR friend_student_no=%s',(project_id, status, self.student_no, self.student_no))




        finally:
            connection.commit()
            connection.close()



    #Öğrencinin arkadaşı var mı kontrolu
    def check_friend(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT * \
            FROM Student \
            WHERE student_no=%s AND friend_student_no IS NOT NULL', (self.student_no,))

            data = cursor.fetchone()
            if data:
                return True

            return False

        finally:
            connection.close()



    #Öğrenci arkadaşlık isteği atıyor
    def send_friend_request(self, friend_student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            #Eklenen kişinin arkadaşı var mı?
            cursor.execute('SELECT * \
            FROM Student \
            WHERE student_no=%s AND friend_student_no IS NOT NULL', (friend_student_no,))


            data = cursor.fetchone()

            if data:
                return "other_friend_exist"




            #Eklenen kişiye daha once istek atildi mi?(Bu kontrol yapilmazsa bir sonki insert into pk hatasi verebilir)
            cursor.execute('SELECT * \
            FROM friend_request \
            WHERE sender_student_no=%s AND receiver_student_no=%s', (self.student_no, friend_student_no))

            data = cursor.fetchone()

            if data:
                return "friend_request_exist"


            #Kurnazlik yapip olmayan ogrenciye istek atarlarsa
            cursor.execute('SELECT * \
            FROM Student \
            WHERE student_no=%s', (friend_student_no,))

            data = cursor.fetchone()

            if not data:
                return "friend_request_exist" #Ayni hatayi veriyor. Mesajin ne oldugu onemli degil sonucta kurnazlik yaptilar


            if data[7]:
                return "project_exist"


            #Eklenen kisi ekleyen kisiye onceden istek atmis mi?
            cursor.execute('SELECT * \
            FROM friend_request \
            WHERE sender_student_no=%s AND receiver_student_no=%s', (friend_student_no, self.student_no))

            data = cursor.fetchone()

            if data:
                return "friend_request_exist_reverse"



            #Arkadaşı yok ise istek set ediliyor
            cursor.execute('INSERT INTO friend_request(receiver_student_no, sender_student_no, status) \
            VALUES (%s,%s,%s)', (friend_student_no, self.student_no,"pending"))

            return None




        finally:
            connection.commit()
            connection.close()


    #Tum ogrencileri dondurur (kendisi disinda)
    def get_all_students(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT student_no,name,sname FROM Student WHERE student_no<>%s',(self.student_no,))
            data = cursor.fetchall()
            return data

        finally:
            connection.close()



    #Ogrenciye arkadaslik istegi atan tum ogrencileri dondurur
    def get_friend_request_senders(self, page_offset):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            query_offset = (page_offset-1)*10

            cursor.execute('SELECT student_no,name,sname FROM Student WHERE student_no IN (\
            SELECT sender_student_no\
            FROM friend_request\
            WHERE receiver_student_no=%s AND status=%s) OFFSET %s LIMIT 11',(self.student_no,"pending",query_offset))

            data = cursor.fetchall()
            return data

        finally:
            connection.close()



    #Ogrenciye yapilan arkadaslik istegini reddetme
    def reject_friend_request(self, sender_student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute('UPDATE friend_request \
            SET status=%s \
            WHERE receiver_student_no=%s AND sender_student_no=%s',("rejected",self.student_no,sender_student_no))

            return True

        finally:
            connection.commit()
            connection.close()


    #Ogrenciye yapilan arkadaslik istegini kabul edip diger tum istekleri reddeder
    def confirm_friend_request(self, sender_student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            #Sender gercekten bize istek atti mi?
            cursor.execute('SELECT * \
            FROM friend_request \
            WHERE sender_student_no=%s AND receiver_student_no=%s',(sender_student_no,self.student_no))

            data = cursor.fetchone()
            if not data:
                return "confirmed_friend_exist"


            #Ekran yenilenmedi, bu sirada isteği atan kisi biri ile arkadas olmus olabilir
            cursor.execute('SELECT friend_student_no \
            FROM Student \
            WHERE student_no=%s',(sender_student_no,))

            data = cursor.fetchone()

            if data[0]:
                return "confirmed_friend_exist"


            cursor.execute('UPDATE friend_request \
            SET status=%s \
            WHERE receiver_student_no=%s AND sender_student_no=%s',("confirmed",self.student_no,sender_student_no))


            #Diger gelen tum istekler reddediliyor
            cursor.execute('UPDATE friend_request \
            SET status=%s \
            WHERE receiver_student_no=%s AND sender_student_no<>%s',("rejected",self.student_no,sender_student_no))


            #Yapılan istekler siliniyor
            cursor.execute('DELETE FROM friend_request \
            WHERE sender_student_no=%s',(self.student_no,))


            #İstegi gonderen kisinin gonderdigi istekler siliniyor.
            cursor.execute('DELETE FROM friend_request \
            WHERE sender_student_no=%s AND receiver_student_no<>%s',(sender_student_no,self.student_no))



            #İstegi gonderen kisiye gelen istekler reddediliyor
            cursor.execute('UPDATE friend_request \
            SET status=%s \
            WHERE receiver_student_no=%s',("rejected",sender_student_no))



            #Kisinin proje bilgileri cekiliyor
            cursor.execute('SELECT project_id,apply_project_id,apply_project_status \
            FROM Student \
            WHERE student_no=%s',(self.student_no,))

            data_you = cursor.fetchone()


            #Son olarak arkadaslik bagi kuruluyor
            cursor.execute('UPDATE Student \
            SET friend_student_no=%s \
            WHERE student_no=%s',(sender_student_no,self.student_no))

            cursor.execute('UPDATE Student \
            SET friend_student_no=%s,project_id=%s,apply_project_id=%s,apply_project_status=%s \
            WHERE student_no=%s',(self.student_no,data_you[0],data_you[1],data_you[2],sender_student_no))



            connection.commit()
            return "success"


        finally:
            connection.close()




    #Ogrencinin arkadaslik istegi attigi kisileri dondurur
    def get_friend_request_receivers(self, page_offset):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            query_offset = (page_offset-1)*10

            cursor.execute('SELECT student_no,name,sname,status FROM Student, friend_request \
            WHERE student_no=receiver_student_no AND sender_student_no=%s OFFSET %s LIMIT 11',(self.student_no, query_offset))

            data = cursor.fetchall()
            return data

        finally:
            connection.close()



    #Ogrencinin gonderdigi arkadaslik istegini iptal eder
    def cancel_friend_request(self, receiver_student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute('DELETE FROM friend_request \
            WHERE receiver_student_no=%s AND sender_student_no=%s AND status<>%s',(receiver_student_no, self.student_no, "confirmed"))


            return "success"

        finally:
            connection.commit()
            connection.close()





    #Ogrencinin arkadasini dondurur
    def get_friend(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT student_no,name,sname FROM Student \
            WHERE friend_student_no=%s',(self.student_no,))

            data = cursor.fetchone()
            return data

        finally:
            connection.close()



    #Proje arkadasini siler
    def delete_friend(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute('SELECT friend_student_no FROM Student \
                        WHERE student_no=%s',(self.student_no,))

            data = cursor.fetchone()


            #Proje alinmissa ve projeye basvurulmussa
            cursor.execute('SELECT project_id,apply_project_id,apply_project_status FROM Student \
                            WHERE student_no=%s',(self.student_no,))

            data_2 = cursor.fetchone()

            ###Onaylanmis proje varsa; kisiye ayni proje bir sonraki indexten verilir
            if data_2[0]:

                #Mevcut proje bilgileri cekiliyor
                cursor.execute('SELECT * FROM Project \
                            WHERE project_id=%s',(data_2[0],))

                data_4 = cursor.fetchone()


                #Basvurulan ana proje bilgileri cekiliyor
                cursor.execute('SELECT * FROM Project \
                            WHERE project_id=%s',(data_2[1],))

                data_3 = cursor.fetchone()

                next_index = 2

                #Akademisyen onerisinden ise
                if data_3[4] == "academician":
                    next_index = data_3[15] + 1

                    #Doluluk guncellemesi
                    cursor.execute('UPDATE Project \
                    SET fullness=fullness+1 WHERE project_id=%s',(data_2[1],))



                #Bir sonraki index ile proje ismi build ediliyor
                new_project_name = data_3[1]+"-"+str(next_index)


                #Bir sonraki indexten proje aciliyor
                cursor.execute('INSERT INTO Project(project_name,project_type,username,proposal_type,form2,form2_status,report1,report1_exist,report2,report2_exist,report3,report3_exist)\
                 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING project_id;',\
                (new_project_name,data_3[2],data_3[3],data_3[4],psycopg2.Binary(data_4[5]),data_4[6],psycopg2.Binary(data_4[7]),data_4[8],psycopg2.Binary(data_4[9]),data_4[10],psycopg2.Binary(data_4[11]),data_4[12]))

                new_project_id = cursor.fetchone()[0]

                #Yeni proje bilgisi arkadaslik istegini silen kisinin projesi olarak set ediliyor
                cursor.execute('UPDATE Student \
                SET project_id=%s WHERE student_no=%s',(new_project_id,self.student_no))





            cursor.execute('DELETE FROM friend_request \
            WHERE (receiver_student_no=%s AND sender_student_no=%s) OR (receiver_student_no=%s AND sender_student_no=%s)',(self.student_no, data[0], data[0], self.student_no))

            cursor.execute('UPDATE Student \
            SET friend_student_no=%s WHERE friend_student_no=%s OR student_no=%s',(None, self.student_no,self.student_no))





            connection.commit()

        finally:
            connection.close()


    def get_report_situations(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT report1_exist,report2_exist,report3_exist FROM Project,Student WHERE student_no=%s AND Student.project_id=Project.project_id', (self.student_no,))
            data=cursor.fetchone()

            return data

        finally:
            connection.close()



    #Ogrencinin projeye devam karari almasi
    def confirm_continuation(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('UPDATE Student \
            SET continuation=%s \
            WHERE (student_no=%s OR friend_student_no=%s) AND apply_project_id IN(SELECT project_id \
            FROM Project \
            WHERE proposal_type=%s)',("true",self.student_no,self.student_no,"academician"))

        finally:
            connection.commit()
            connection.close()


    #Bu metot objenin uye alanlarini sinif icerisinde set edip, objeyi return etmektedir.
    @classmethod
    def find_by_student_no(cls, student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT student_no,password,name,sname,continuation FROM Student WHERE student_no=%s', (student_no,))
            data = cursor.fetchone()
            if data:
                #cls mevcut sinifin contructor ini temsil etmektedir
                instance = cls(data[0], data[1], data[2], data[3], data[4])
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
    def get_projects(self, page_offset):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            query_offset = (page_offset-1)*10

            cursor.execute('SELECT project_id,project_name,project_type,capacity,fullness \
            FROM Academician,Project \
            WHERE Academician.username=%s AND \
            Project.username=Academician.username AND \
            proposal_type=%s AND capacity IS NOT NULL OFFSET %s LIMIT 11', (self.username, "academician", query_offset))

            data = cursor.fetchall()

            return data
        finally:
            connection.close()




    def delete_project(self, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('DELETE FROM Project \
            WHERE project_id=%s AND \
            username=%s ',(project_id,self.username))

            return True

        finally:
            connection.commit()
            connection.close()



    #Akademisyenin proje onerisi icin
    def propose_project(self, project_name, project_type, capacity):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('INSERT INTO Project(project_name, project_type, username, proposal_type, app_count,fullness,capacity)\
            VALUES (%s,%s,%s,%s)', (project_name, project_type, self.username, "academician",0,0,capacity) )


        finally:
            connection.commit()
            connection.close()





    #Gets Academician's students' numbers.
    def get_students(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute(
            'SELECT student_no,Student.name,Student.sname,Project.project_name,Project.project_type FROM Student,Project,Academician WHERE Academician.username=%s AND \
            Academician.username=Project.username AND \
            Student.project_id=Project.project_id', (self.username,))

            data = cursor.fetchall()

            student_list = []

            if data:
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



    #Akademisyene ait projeyi gelen parametrelerle gunceller
    def set_project(self, project_id, new_project_name, new_project_type, new_project_capacity):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('UPDATE Project \
            SET project_name=%s, project_type=%s, capacity=%s \
            WHERE project_id=%s AND \
            username=%s ',(new_project_name, new_project_type, new_project_capacity, project_id, self.username))

            return True

        finally:
            connection.commit()
            connection.close()



    #Ogrencinin projesi set edilir (Proje başvurusu kabul edildi)
    def set_student_project(self, student_no, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT apply_project_id\
            FROM Student WHERE student_no=%s', (student_no,) )

            data = cursor.fetchone()

            if data[0] is None:
                return "apply_canceled"


            #Ana projenin bilgileri cekiliyor
            cursor.execute('SELECT project_name,project_type,proposal_type,fullness,capacity\
            FROM Project WHERE project_id=%s', (project_id,) )

            set_project_id = project_id

            data = cursor.fetchone()

            #Eger basvuru yapilmis proje akademisyen onerisinden ise
            if data[2] == "academician":
                #Eger belirlenen max kapasiteye ulasilmis ise. Hata donduruluyor
                if data[3] == data[4]:
                    return "max_capacity"


                #Yeni olusturulan projenin adi siradaki indexe gore belirleniyor
                next_index = data[3]+1
                new_project_name = data[0]+"-"+str(next_index)

                #Siradaki proje indexine gore yeni proje olusturuluyor.
                cursor.execute('INSERT INTO Project(project_name, project_type, username, proposal_type)\
                VALUES (%s,%s,%s,%s) RETURNING project_id;', (new_project_name, data[1], self.username, data[2]) )

                set_project_id = cursor.fetchone()[0]

                #Proje doluluk ve basvuru sayi bilgileri guncelleniyor
                cursor.execute('UPDATE Project \
                SET fullness=fullness+1, app_count=app_count-1 \
                WHERE project_id=%s',(project_id,))


            #Proje set ediliyor
            cursor.execute('UPDATE Student \
            SET project_id=%s, apply_project_status=%s,continuation=%s \
            WHERE (student_no=%s OR friend_student_no=%s) AND apply_project_id IN (SELECT project_id \
            FROM Project,Academician \
            WHERE Project.username=Academician.username AND Project.username=%s)',(set_project_id, "confirmed",None ,student_no, student_no, self.username))


            return "no_problem"

        finally:
            connection.commit()
            connection.close()




    #Ogrencinin proje başvurusu reddediliyor
    def reject_student_project_application(self, student_no):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            #Proje başvuru durumu guncelleniyor
            cursor.execute('UPDATE Student \
            SET apply_project_status=%s,continuation=%s \
            WHERE (student_no=%s OR friend_student_no=%s) AND apply_project_id IN (SELECT project_id \
            FROM Project,Academician \
            WHERE Project.username=Academician.username AND Project.username=%s)',("rejected",None ,student_no, student_no, self.username))

            #Basvuru sayisi guncelleniyor
            cursor.execute('UPDATE Project \
            SET app_count=app_count-1 \
            WHERE  project_id IN (SELECT apply_project_id \
            FROM Student \
            WHERE student_no=%s)',(student_no,))


            return True

        finally:
            connection.commit()
            connection.close()




    #Akademisyenin başvurulan tüm projelerini döndürür. Öğrenci önerisinden de olanlar dahil.
    def get_all_applied_projects(self, page_offset):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            query_offset = (page_offset-1)*10

            cursor.execute('SELECT project_id, project_name, project_type, proposal_type,capacity,fullness \
            FROM Project \
            WHERE username=%s AND project_id IN (SELECT apply_project_id \
            FROM Student WHERE apply_project_status=%s) OFFSET %s LIMIT 11', (self.username, "pending", query_offset))

            data = cursor.fetchall()

            return data

        finally:
            connection.close()



    #Akademisyene bağlı projelere başvuran tüm öğrencileri döndürür
    def get_project_application_students(self, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT student_no, name, sname, friend_student_no,continuation \
            FROM Student \
            WHERE apply_project_id=%s AND apply_project_status=%s', (project_id, "pending"))

            data = cursor.fetchall()

            return data

        finally:
            connection.close()


    #Tum akademisyenleri dondurur
    @classmethod
    def get_all_academicians(cls):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT username, name, sname FROM Academician')
            data = cursor.fetchall()
            if data:

                return data
        finally:
            connection.close()



    #Form-2 si onay bekleyen projeleri dondurur
    def get_form2_pending_projects(self, page_offset):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            query_offset = (page_offset-1)*10

            cursor.execute('SELECT project_id,project_name,project_type \
            FROM Academician,Project \
            WHERE Academician.username=%s AND \
            Project.username=Academician.username AND \
            form2_status=%s \
            OFFSET %s LIMIT 11', (self.username, "academician_pending", query_offset))

            data = cursor.fetchall()

            if data:
                return data
        finally:
            connection.close()



    #Ogrenci Form-2 si onaylanir
    def confirm_form2(self, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute('UPDATE Project \
            SET form2_status=%s \
            WHERE username=%s AND project_id=%s',("council_pending",self.username,project_id))

            return True

        finally:
            connection.commit()
            connection.close()




    #Ogrenci Form-2 si reddedilir
    def reject_form2(self, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute('UPDATE Project \
            SET form2_status=%s \
            WHERE username=%s AND project_id=%s',("academician_rejected",self.username,project_id))

            return True

        finally:
            connection.commit()
            connection.close()


    #Gets report with given report type
    def get_report(self, report_type, project_id):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()

        try:

            cursor.execute(
            sql.SQL("SELECT {} FROM Project WHERE username=%s AND project_id=%s").format(
            sql.Identifier(report_type)), (self.username, project_id))

            data = cursor.fetchone()

            if data:

                return data[0]
        finally:
            connection.close()


    #Akademisyene bagli projelerden en az bir raporu yuklenmis olanlari dondurur
    def get_all_projects_with_report(self):
        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
        cursor = connection.cursor()


        try:
            cursor.execute('SELECT project_id,project_name,project_type \
            FROM Project \
            WHERE username=%s AND (report1_exist=%s OR report2_exist=%s OR report3_exist=%s)', (self.username, "true","true","true" ))

            data = cursor.fetchall()

            return data
        finally:
            connection.close()


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
