from flask import Flask, redirect, url_for, request, render_template, send_from_directory, session, send_file
from werkzeug.utils import secure_filename
#Dosya islemleri icin
import os
from os import listdir
from os.path import isfile, join
from flask_session import Session
#Kullanici islemleri icin
from user_authentication import *
from werkzeug.security import generate_password_hash, check_password_hash
from add_user_to_database import *
import json
from io import BytesIO
import datetime
import zipfile
import time
from process import *
import re


app = Flask(__name__)


#SESSION AYARLARI
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(app.root_path,"session_files")
app.config.from_object(__name__)
Session(app)



#UPLOAD DOSYA AYARLARI
UPLOAD_FOLDER = os.path.abspath(os.path.join(app.root_path, 'uploads'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




#KARSILAMA SAYFASI
@app.route('/')
def greeting():
    #return render_template("index.html")
    if session.get("logged_in"):

        user = session["user"]
        user_type= session["user_type"]

        template_values_curr = {
            "first_timer":user.first_timer,
            "user_type":user_type
        }

        template_values = {
        "name":user.name,
        "sname":user.sname,
        "user_type":user_type,
        "PROCESS_1":PROCESS_1,
        "PROCESS_2":PROCESS_2,
        "PROCESS_3":PROCESS_3,
        "PROCESS_4":PROCESS_4,
        "PROCESS_5":PROCESS_5,
        "PROCESS_6":PROCESS_6,
        "PROCESS_7":PROCESS_7
        }

        return render_template("index.html", template_values=template_values, template_values_curr=json.dumps(template_values_curr) )

    return redirect(url_for("login_handle"))






#KULLANICI LOGIN HANDLE
@app.route('/login', methods = ["GET","POST"])
def login_handle():
    if request.method == "GET":
        return render_template("login.html",login_failure="no_failure")

    else:
        #username_student_no can be username or student_no
        username_student_no = request.form['username']
        password = request.form['password']

        tip = None

        if re.search("^[0-9]{7}",username_student_no):
            user = Student.find_by_student_no(username_student_no)
            tip = "student"

        else:
            user = Academician.find_by_username(username_student_no)
            tip = "academician"


        if user and check_password_hash(user.password, password):
            #Kullanici hesabi aktif mi?
            if (tip=="student") and user.active == "false":
                return render_template("login.html", login_failure="not_active")

            else:
                #Mevcut kullanici objesi session'da kaydediliyor
                session["user"] = user
                session["logged_in"] = True
                session["user_type"] = tip

                return redirect(url_for("greeting"))


        session["login_failure"] = True
        return render_template("login.html", login_failure="not_exist")



#KULLANICI REGISTER HANDLE
@app.route('/register', methods = ["GET","POST"])
def register_handle():
    if request.method == "GET":
        return render_template("register.html",error_source="no_error",success=False)

    #POST
    else:
        student_no = request.form['student_no']

        if re.search("^[0-9]?[0-9]011[0-9]{3}$",student_no):
            error = Student.register_student(student_no)
            if error:
                return render_template("register.html",error_source="user_exists",success=False)

            return render_template("register.html",error_source="no_error",success=True)


        return render_template("register.html",error_source="wrong_format",success=False)



#LOGOUT HANDLE
@app.route('/logout')
def logout_handle():
    session.pop("logged_in", None)
    session.pop("login_failure", None)
    session.pop("user", None)
    session.pop("user_type", None)
    return redirect(url_for("greeting"))

#Profil Handle
@app.route('/Profil')
def show_profile():
    #Giris yapildi mi???
    if session.get("logged_in"):
        user = session["user"]
        template_values={
            "user_type":session["user_type"],
            "PROCESS_1":PROCESS_1,
            "PROCESS_2":PROCESS_2,
            "PROCESS_3":PROCESS_3,
            "PROCESS_4":PROCESS_4,
            "PROCESS_5":PROCESS_5,
            "PROCESS_6":PROCESS_6,
            "PROCESS_7":PROCESS_7
        }
        kisiselBilgiler={
            "Ad" : user.name,"Soyad":user.sname
        }
        return render_template("profil.html",infoAboutUser=kisiselBilgiler,template_values=(template_values))

    #Giris yapilmadiysa giris sayfasina yonlendirilir.
    return redirect(url_for("login_handle"))

#Duyuru Olusturma Sayfasina Yonlendirme
@app.route('/Notices/CreateNotice')
def createNotice():
    if session.get("logged_in"):
        if session["user_type"] == "student":
            return redirect(url_for("greeting"))
        else:
            user1 = session["user"]
            template_values={
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }
            return render_template("createNoticePage.html",template_values=template_values)
    return redirect(url_for("login_handle"))

#Duyuruyu veri tabanına kaydedelim
@app.route('/Notices/PublishNotice',methods=["POST"])
def saveNotice():
    if request.method=="POST":
        if session.get("logged_in"):
            user1 = session["user"]
            template_values={
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }
            akademisyenAdi = user1.username

            current_date_time = datetime.datetime.today()
            noticeTime= '{:%d/%m/%y %H:%M}'.format(current_date_time)
            title = request.form["title"]
            cont = request.form["contentNotice"]
            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

            cursor = connection.cursor()

            try:

                cursor.execute("INSERT INTO notice(title,content,date,username) VALUES(%s,%s,%s,%s)",(title,cont,noticeTime,akademisyenAdi))
            finally:
                connection.commit()
                connection.close()


    return redirect(url_for("createNotice"))

#Akademisyenin kendi yayinladigi duyurulari gormesi
@app.route('/Notices/MyNotices')
def showMyNotices():
    if session.get("logged_in"):
        user1 = session["user"]
        template_values={
            "user_type":session["user_type"],
            "PROCESS_1":PROCESS_1,
            "PROCESS_2":PROCESS_2,
            "PROCESS_3":PROCESS_3,
            "PROCESS_4":PROCESS_4,
            "PROCESS_5":PROCESS_5,
            "PROCESS_6":PROCESS_6,
            "PROCESS_7":PROCESS_7
        }
        if session["user_type"] == "student":
            Academician_userName = user1.get_academician()
        else:
            Academician_userName = user1.username

        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

        cursor = connection.cursor()

        try:

            cursor.execute(
                'SELECT n.id,n.title,n.content,n.date from notice n where n.username=%s order by n.date desc',(Academician_userName,))

            data = cursor.fetchall()
            num_of_notices=len(data)
            disable_next_page = False
            if num_of_notices < 11:
                disable_next_page = True
            if((request.args.get("page"))==None):
                pageno=1
            else:
                pageno=int(request.args.get("page"))
            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                "error":False,
                "notices":data,
                "disable_next_page":disable_next_page,
                "init_page_num":pageno
            }
        finally:
            connection.close()
        return render_template("myNoticePage.html",template_values=template_values,template_values_curr=json.dumps(template_values_curr))

    return redirect(url_for("login_handle"))

#Duyuru iceriginin guncellenmesi
@app.route('/Notices/EditNotice',methods=["GET"])
def updateNotice():
    if request.method == 'GET':
        if session.get("logged_in"):
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))
            else:
                content = (request.args.get("msg"))
                id = int(request.args.get("id"))

                current_date_time = datetime.datetime.today()
                noticeTime= '{:%d/%m/%y %H:%M}'.format(current_date_time)

                connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

                cursor = connection.cursor()

                try:

                    cursor.execute("UPDATE notice SET content=%s,date=%s where id="+str(id),(content,noticeTime,))
                    connection.commit()
                finally:
                    connection.close()


                return redirect(url_for("showMyNotices"))

        return redirect(url_for("login_handle"))
    return redirect(url_for("showMyNotices"))

#Admin tarafindan duyuru olusturulmasi
@app.route('/Notices/CreateGeneralNotice')
def createGeneralNotice():
    #Giris yapildi mi?
    if session.get("admin_logged_in"):
        return render_template("createGeneralNoticePage.html")


    return redirect(url_for("admin_login_handle"))

#Admin tarafindan olusturulan duyurunun veritabanına kaydı
@app.route('/Notices/PublishGeneralNotice',methods=['POST'])
def saveGeneralNotice():
    if request.method=="POST":
        if session.get("admin_logged_in"):

            userName = 'Admin'

            current_date_time = datetime.datetime.today()
            noticeTime= '{:%d/%m/%y %H:%M}'.format(current_date_time)
            title = request.form["title"]
            cont = request.form["contentNotice"]

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

            cursor = connection.cursor()

            try:

                cursor.execute("INSERT INTO notice(title,content,date,username) VALUES(%s,%s,%s,%s)",(title,cont,noticeTime,userName))
                connection.commit()
            finally:
                connection.close()
    return redirect(url_for("createGeneralNotice"))

#Kullanicilarin Admin in yayinladigi duyurulari goruntuleyebilmesi
@app.route('/Notices/GeneralNotices')
def showGeneralNoticestoUsers():
    if session.get("logged_in"):

        template_values={
            "user_type":session["user_type"],
            "PROCESS_1":PROCESS_1,
            "PROCESS_2":PROCESS_2,
            "PROCESS_3":PROCESS_3,
            "PROCESS_4":PROCESS_4,
            "PROCESS_5":PROCESS_5,
            "PROCESS_6":PROCESS_6,
            "PROCESS_7":PROCESS_7
        }

        userName = 'Admin'

        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

        cursor = connection.cursor()

        try:

            cursor.execute(
                'SELECT n.id,n.title,n.content,n.date from notice n where n.username=%s order by n.date desc',(userName,))

            data = cursor.fetchall()
            num_of_notices=len(data)
            disable_next_page = False
            if num_of_notices < 11:
                disable_next_page = True
            if((request.args.get("page"))==None):
                pageno=1
            else:
                pageno=int(request.args.get("page"))
            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                "error":False,
                "notices":data,
                "disable_next_page":disable_next_page,
                "init_page_num":pageno
            }

        finally:
            connection.close()

        return render_template("GeneralNoticePage.html",template_values=template_values,template_values_curr=json.dumps(template_values_curr))

    return redirect(url_for("login_handle"))



#Admin in duyurulari goruntulemesi
@app.route('/Notices/MyGeneralNotices')
def showMyGeneralNotices():
    if session.get("admin_logged_in"):

        userName = 'Admin'

        connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

        cursor = connection.cursor()

        try:

            cursor.execute(
                'SELECT n.id,n.title,n.content,n.date from notice n where n.username=%s order by n.date desc',(userName,))

            data = cursor.fetchall()
            num_of_notices=len(data)
            disable_next_page = False
            if num_of_notices < 11:
                disable_next_page = True
            if((request.args.get("page"))==None):
                pageno=1
            else:
                pageno=int(request.args.get("page"))
            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                "error":False,
                "notices":data,
                "disable_next_page":disable_next_page,
                "init_page_num":pageno
            }
        finally:

            connection.close()

        return render_template("myGeneralNoticePage.html",template_values_curr=json.dumps(template_values_curr))

    return redirect(url_for("admin_login_handle"))

#Duyuru iceriginin admin tarafindan guncellenmesi
@app.route('/Notices/EditGeneralNotice',methods=["GET"])
def updateGeneralNotice():
    if request.method == 'GET':
        if session.get("admin_logged_in"):

            content = (request.args.get("msg"))
            id = int(request.args.get("id"))

            current_date_time = datetime.datetime.today()
            noticeTime= '{:%d/%m/%y %H:%M}'.format(current_date_time)

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

            cursor = connection.cursor()

            try:

                cursor.execute("UPDATE notice SET content=%s,date=%s where id="+str(id),(content,noticeTime,))
                connection.commit()

            finally:
                connection.close()

            return redirect(url_for("showMyGeneralNotices"))

        return redirect(url_for("admin_login_handle"))
    return redirect(url_for("showMyGeneralNotices"))


#Akademisyenden proje alanlarin listesi
@app.route('/Grades/NotGirisSayfasi',methods=["GET"])
def ShowMyStudents():
    if request.method=="GET":
        if session.get("logged_in"):
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))
            else:
                user1 = session["user"]
                template_values={
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7
                }
                akademisyenAdi = user1.username

                connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

                cursor = connection.cursor()

                try:

                    cursor.execute(
                    'SELECT student_no,Student.name,Student.sname,Project.project_name,Project.project_type FROM Student,Project,Academician WHERE Academician.username=%s AND \
                    Academician.username=Project.username AND \
                    Student.project_id=Project.project_id AND Student.grade is NULL', (akademisyenAdi,))

                    data = cursor.fetchall()
                    #students = academician.get_students()
                    #hocanin proje verdigi ogrencisi olmayabilir
                    num_of_students=len(data)
                    disable_next_page = False
                    if num_of_students < 11:
                        disable_next_page = True
                    if((request.args.get("page"))==None):
                        pageno=1
                    else:
                        pageno=int(request.args.get("page"))
                    #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                    template_values_curr = {
                        "error":False,
                        "students":data,
                        "disable_next_page":disable_next_page,
                        "init_page_num":pageno
                    }

                finally:
                    connection.close()

                return render_template("gradePage.html",template_values=template_values,template_values_curr=json.dumps(template_values_curr))
        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))
#Girilen Notu Sisteme Ekleyelim
@app.route('/Grades/NotuSistemeEkle',methods=["GET","POST"])
def notuKaydet():
    if request.method == 'GET':
        if session.get("logged_in"):
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))
            else:
                student_no = (request.args.get("sno"))
                grade1 = int(request.args.get("grade"))
                user = session["user"]
                akademisyenAdi = user.username
                academician = Academician.find_by_username(akademisyenAdi)

                academician.set_grade(student_no,grade1)

                return redirect(url_for("ShowMyStudents"))


        return redirect(url_for("login_handle"))
    return redirect(url_for("ShowMyStudents"))

#Akademisyenden proje notları girilmiş öğrenciler
@app.route('/Grades/NotDüzenle',methods=["GET"])
def ShowMyStudentsGrade():
    if request.method=="GET":
        if session.get("logged_in"):
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))
            else:
                user1 = session["user"]
                template_values={
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7
                }
                akademisyenAdi = user1.username
                academician = Academician.find_by_username(akademisyenAdi)

                connection = psycopg2.connect(DATABASE_URL, sslmode='allow')

                cursor = connection.cursor()

                try:

                    cursor.execute(
                    'SELECT student_no,Student.name,Student.sname,Project.project_name,Project.project_type,Student.grade FROM Student,Project,Academician WHERE Academician.username=%s AND \
                    Academician.username=Project.username AND \
                    Student.project_id=Project.project_id AND Student.grade is not NULL', (akademisyenAdi,))

                    data = cursor.fetchall()
                    #students = academician.get_students()
                    #hocanin proje verdigi ogrencisi olmayabilir
                    num_of_students=len(data)
                    disable_next_page = False
                    if num_of_students < 11:
                        disable_next_page = True
                    if((request.args.get("page"))==None):
                        pageno=1
                    else:
                        pageno=int(request.args.get("page"))
                    #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                    template_values_curr = {
                        "error":False,
                        "students":data,
                        "disable_next_page":disable_next_page,
                        "init_page_num":pageno
                    }
                    return render_template("gradePage2.html",template_values=template_values,template_values_curr=json.dumps(template_values_curr))
                finally:
                    connection.close()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))

#Ogrenci Kendi Notunu Görüntülemek Isterse
@app.route('/Grades/MyGrade')
def showMyGrade():
    #Giris yapildi mi???
    if session.get("logged_in"):
        if(session["user_type"]=="student"):
            user = session["user"]
            std = Student.find_by_student_no(user.student_no)
            myGrade1 = std.get_grade()
            if(myGrade1==None):
                myGrade1 = -1
            template_values={
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7,
                "PROCESS_8":PROCESS_8
            }
            kisiselBilgiler={
                "Ad" : user.name,"Soyad":user.sname,"Notu":myGrade1
            }

            data_project = user.get_applied_project()
            template_values_curr = {
                "PROCESS_8":PROCESS_8,
                "std_no":user.student_no,
                "data_project":data_project,
                "confirm_status":std.continuation
            }
            return render_template("myGradePage.html",infoAboutUser=kisiselBilgiler,template_values=(template_values),template_values_curr=json.dumps(template_values_curr))
        return redirect(url_for("greeting"))
    #Giris yapilmadiysa giris sayfasina yonlendirilir.
    return redirect(url_for("login_handle"))


#Düzenlenen notu Sisteme Girelim
@app.route('/Grades/GradeEdit',methods=["GET","POST"])
def notuDüzelt():
    if request.method == 'GET':
        if session.get("logged_in"):
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))
            else:
                student_no = (request.args.get("sno"))
                grade1 = int(request.args.get("grade"))
                user = session["user"]
                akademisyenAdi = user.username
                academician = Academician.find_by_username(akademisyenAdi)

                academician.set_grade(student_no,grade1)

                return redirect(url_for("ShowMyStudentsGrade"))


        return redirect(url_for("login_handle"))
    return redirect(url_for("ShowMyStudentsGrade"))



#ADMIN PANELI INDEX
@app.route('/admin',methods=["GET","POST"])
def admin_index_handle():

    if request.method == "GET":

        if session.get("admin_logged_in"):

            template_values={
            "message":""
            }

            return render_template("admin_index.html",template_values=json.dumps(template_values))

        return redirect(url_for("admin_login_handle"))

    #POST
    else:

        if session.get("admin_logged_in"):
            #Ogrenci veya akademisten bilgileri formdan cekiliyor
            student_no_username = request.form["student_no_username"]
            name = request.form["name"]
            sname = request.form["sname"]
            email = request.form["email"]
            user_type = request.form['tipsec']

            error_source = "mail"


            try:

                admin = Admin()

                #Turkce karakter kontrolu. Mail gonderirken turkce karakter sikinti oluyor.
                if not (all(ord(char) < 128 for char in student_no_username)):

                    template_values={
                    'message':"error",
                    'error':"Kullanici adinda turkce karakter bulunmamali!"
                    }

                    return render_template("admin_index.html",template_values=json.dumps(template_values))


                admin.generated_password = admin.generate_random_password()

                #SMTP server giris
                server = smtplib.SMTP("smtp.gmail.com:587")
                server.ehlo()
                server.starttls()
                server.login(session["admin_username"], session["admin_password"])


                #Kullaniciya sifresini mail ile  gonderme islemi
                body ="Merhaba " + student_no_username + ",\n\n" + admin.generated_password + " sifresi ile sisteme giris yapabilirsiniz.\n\nYTU Proje Takip Sistemi Ekibi"
                message="Subject: {}\n\n{}".format("YTU Proje Takip Sistemi Hesap Sifreniz", body)
                server.sendmail(session["admin_username"], email, message)
                server.quit()


                error_source = "database"

                #Veri tabanina yazma islemi
                admin.write_db(user_type, student_no_username, name, sname)


                template_values = {
                'message':"success"
                }


                return render_template("admin_index.html",template_values=json.dumps(template_values))

            except Exception as e:
                student_no_username = request.form["student_no_username"]

                if error_source == "mail":
                    error_message = "Kullanıcıya şifresi mail ile gönderilemedi. Lütfen tekrar deneyiniz."

                elif error_source == "database":
                    error_message = student_no_username + " kullanici adlı/ögrenci nolu kullanici veri tabanında kayıtlıdır!"



                template_values={
                'message':"error",
                'error':error_message
                }

                return render_template("admin_index.html",template_values=json.dumps(template_values))




        else:
            return redirect(url_for("admin_login_handle"))






#ADMIN PANELI GIRIS
@app.route('/admin/login',methods=["GET","POST"])
def admin_login_handle():

    if request.method == "GET":

        session["login_failure"] = False

        #Admin girisi yapildi mi?
        if session.get("admin_logged_in"):

            template_values={
            "message":""
            }

            return render_template("admin_index.html")

        return render_template("admin_login.html")

    #POST
    else:
        username_form = request.form['admin_username']
        password_form = request.form['admin_password']


        if check_password_hash(admin_password_hash,password_form) and check_password_hash(admin_username_hash,username_form):
            session["admin_logged_in"] = True
            session["admin_username"] = username_form
            session["admin_password"] = password_form
            return redirect(url_for("admin_index_handle"))


        session["admin_login_failure"] = True
        return render_template("admin_login.html", admin_login_failure=session["admin_login_failure"])






#ADMIN PANELI CIKIS
@app.route('/admin/logout',methods=["GET"])
def admin_logout_handle():
    session.pop("admin_logged_in",None)
    session.pop("admin_username",None)
    session.pop("admin_password",None)
    return redirect(url_for("admin_login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Akademisyen Proje Önerileri
#Sorumlu kişi: Çetin Tekin
@app.route('/project/academician_proposals',methods=["GET"])
def project_academician_proposals_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("logged_in"):

            #NOT: Bu kisimda SQL sorgusu yazilmistir. Cunku Genel Projelerin listelenebilmesi icin Student veya Academician instance
            #methodlari kullanilamaz, bunun icin generic bir method yazilmadi.

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            page_offset = int(request.args.get("page"))
            query_offset = (page_offset-1)*10

            try:
                cursor.execute('SELECT project_id,project_name,project_type,username,proposal_type FROM Project WHERE proposal_type=%s AND capacity IS NOT NULL OFFSET %s LIMIT 11',("academician",query_offset))

                #data listelerin listesi
                data = cursor.fetchall()

                num_of_projects = len(data)

                disable_next_page = False

                if num_of_projects < 11:
                    disable_next_page = True
                    #Son eleman silinir


                else:
                    data = data[:-1]




                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "error":False,
                    "projects":data,
                    "disable_next_page":disable_next_page,
                    "init_page_num":int(request.args.get("page"))

                }

                return render_template("academician_proposals.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


            except Exception as e:

                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "error":True

                }

                return render_template("academician_proposals.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )

            finally:
                connection.close()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))








#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Öner
#Sorumlu kişi: Çetin Tekin
@app.route('/project/propose_project',methods=["GET","POST"])
def academician_propose_project_handler():
    if request.method == "GET":

        #Surec acik degil ise
        if not PROCESS_1:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):
            try:

                #Ogrenciler bu sayfaya girmeye calisirsa ana sayfaya atiliyor
                if session["user_type"] == "student":
                    return redirect(url_for("greeting"))


                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "success":False

                }

                return render_template("propose_project.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


            except Exception as e:

                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "success":False

                }

                return render_template("propose_project.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



    if request.method == "POST":

        #Surec acik degil ise
        if not PROCESS_1:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            try:

                #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
                if session["user_type"] == "student":
                    return redirect(url_for("greeting"))



                #Mevcut sessiondan akademisyen nesnesi cekiliyor.
                academician = session["user"]
                project_name = request.form["project_name"]
                project_type = request.form["tipsec"]
                capacity = request.form["project_capacity"]


                success = True

                if re.search("^[1-9][0-9]*$", capacity) is None:
                    success = False

                if success:
                    capacity = int(capacity)
                    #Veri tabani kaydi
                    academician.propose_project(project_name, project_type, capacity)



                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "success":success

                }


                return render_template("propose_project.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


            except Exception as e:

                #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
                template_values_index = {
                    "user_type":session["user_type"],
                    "PROCESS_1":PROCESS_1,
                    "PROCESS_2":PROCESS_2,
                    "PROCESS_3":PROCESS_3,
                    "PROCESS_4":PROCESS_4,
                    "PROCESS_5":PROCESS_5,
                    "PROCESS_6":PROCESS_6,
                    "PROCESS_7":PROCESS_7

                }
                return (str(e))


                #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
                template_values_curr = {
                    "Success":False

                }

                return render_template("propose_project.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))








#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Önerilen Projelerim
#Sorumlu kişi: Çetin Tekin
@app.route('/project/my_proposals',methods=["GET"])
def academician_my_proposals_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("logged_in"):


            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))



            page_offset = int(request.args.get("page"))

            #Mevcut sessiondan akademisyen nesnesi cekiliyor.
            academician = session["user"]

            projects = academician.get_projects(page_offset)
            disable_next_page = False

            #Proje önerisi varsa
            if projects:

                num_of_projects = len(projects)
                if num_of_projects < 11:
                    disable_next_page = True


                else:
                    #Son eleman silinir
                    projects = projects[:-1]





            #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7

            }


            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                    "projects":projects,
                    "disable_next_page":disable_next_page,
                    "init_page_num":int(request.args.get("page")),
                    "PROCESS_1":PROCESS_1

            }

            return render_template("my_proposals.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )





        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))







#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Önerilen Projelerim, proje silme işlemi için AJAX call aracılığı ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/delete_proposal',methods=["GET"])
def academician_delete_proposal_handler():
    if request.method == "GET":

        #Surec acik degil ise
        if not PROCESS_1:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            project_id = request.args.get("project_id")
            project_id = int(project_id)

            academician  = session["user"]

            success = academician.delete_project(project_id)

            success = {
            "success":success
            }

            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Önerilen Projelerim, proje düzenleme işlemi için AJAX call aracılığı ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/edit_proposal',methods=["POST"])
def academician_edit_proposal_handler():
    if request.method == "POST":

        #Giris yapildi mi?
        if session.get("logged_in"):

            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))



            project_id = request.json['project_id']
            new_project_name = request.json['new_project_name']
            new_project_type = request.json['new_project_type']
            new_project_capacity = request.json['new_project_capacity']
            new_project_capacity = int(new_project_capacity)

            academician  = session["user"]

            success = academician.set_project(project_id, new_project_name, new_project_type, new_project_capacity)

            success = {
                "success":success
            }

            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Form-2 Gönder
#Sorumlu kişi: Çetin Tekin
@app.route('/project/send_form2',methods=["GET","POST"])
def student_send_form2_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_4:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            user = session["user"]

            project = user.get_project()

            template_values_curr = {}


            #PROJEYE BAGLI MI? KONTROLU
            if project:
                template_values_curr["project_exists"] = True


            else:
                template_values_curr["project_exists"] = False





            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("send_form2.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))


    #METHOD POST
    else:

        #Surec acik mi?
        if not PROCESS_4:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            user = session["user"]

            #Projeye bagli degil ise sayfaya tekrar atiliyor
            project = user.get_project()
            if not project:
                return redirect(url_for("greeting"))


            project_id = project.project_id


            f = request.files['file_to_send']
            form2_blob_data = f.read()


            response = user.add_form2(form2_blob_data)


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }

            template_values_curr = {
                "project_exists":True,
                "success":True
            }


            return render_template("send_form2.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gönderilen Form-2
#Sorumlu kişi: Çetin Tekin
@app.route('/project/view_form2',methods=["GET"])
def student_view_form2_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            user = session["user"]

            project = user.get_project()

            template_values_curr = {}


            #PROJEYE BAGLI MI? KONTROLU
            if project:
                template_values_curr["project_exists"] = True
                template_values_curr["form2_exists"] = project.form2_exists



            else:
                template_values_curr["project_exists"] = False




            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("send_form2.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gönderilen Form-2'de butona tıklamayla yapılan AJAX call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/download_report',methods=["GET"])
def download_report_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("logged_in"):

            user = session["user"]
            user_type = session["user_type"]
            report_type = request.args.get("report_type")
            project_id = request.args.get("project_id")

            if user_type == "student":
                report = user.get_report(report_type)


            else:
                report = user.get_report(report_type, project_id)



            return send_file(BytesIO(report), attachment_filename=report_type+".pdf", as_attachment=True)



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Başvurusu Yap
#Sorumlu kişi: Çetin Tekin
@app.route('/project/apply_project',methods=["GET","POST"])
def apply_project_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_2:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            #POST METOTTAN GELEN PARAMETRELER
            success = request.args.get("success")
            capacity_full = request.args.get("capacity_full")
            app_cnt_limit = request.args.get("app_cnt_limit")
            apply_exist = request.args.get("apply_exist")

            success = str(success)

            #Akademisyen önerileri çekiliyor
            projects = Project.get_academician_proposals()

            #Akademisyen bilgileri çekiliyor
            academicians = Academician.get_all_academicians()



            template_values_curr = {
                "projects":projects,
                "academicians":academicians,
                "success":success,
                "capacity_full":capacity_full,
                "app_cnt_limit":app_cnt_limit,
                "apply_exist":apply_exist
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("apply_project.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))


    #post method
    else:

        #Surec acik mi?
        if not PROCESS_2:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            proposal_type = request.form['proposal_type_select']
            user = session["user"]

            if user.get_applied_project():
                return redirect("/project/apply_project?success=false&apply_exist=true")


            try:
                #Proje akademisyen önerisinden başvuruldu
                if proposal_type == "academician_proposal":

                    project_id = request.form["project_choice"]
                    project_id = int(project_id)

                    capacity_full = Project.check_project_capacity(project_id)

                    if capacity_full:
                        return redirect("/project/apply_project?success=false&capacity_full=true")


                    user.apply_academician_project(project_id)


                elif proposal_type == "student_proposal":

                    project_name = request.form["project_name"]
                    project_type = request.form["project_type_choice"]
                    academician_username = request.form["academician_choice"]
                    user.apply_student_project(project_name, project_type, academician_username)


                return redirect("/project/apply_project?success=true")



            except Exception as e:
                return redirect("/project/apply_project?success=false")
                #return (str(e))




        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Başvurusu Durumu
#Sorumlu kişi: Çetin Tekin
@app.route('/project/project_apply_status',methods=["GET"])
def project_apply_status_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            user = session["user"]
            project_info = user.get_applied_project()


            template_values_curr = {
                "project_info":project_info,
                "PROCESS_2":PROCESS_2
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("project_apply_status.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Başvurusu Durumu AJAX call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/delete_project_apply',methods=["GET"])
def project_apply_cancel_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_2:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            user = session["user"]
            user.delete_project_apply()

            return "success"



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))







#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Öğrenci Proje Başvuruları (Akademisyen)
#Sorumlu kişi: Çetin Tekin
@app.route('/project/student_project_applications',methods=["GET"])
def student_project_applications_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_3:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Öğrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            academician = session["user"]
            page_offset = int(request.args.get("page"))
            applied_projects = academician.get_all_applied_projects(page_offset)

            disable_next_page = False

            #Proje başvurusu varsa
            if applied_projects:

                num_of_projects = len(applied_projects)
                if num_of_projects < 11:
                    disable_next_page = True


                else:
                    #Son eleman silinir
                    applied_projects = applied_projects[:-1]




            template_values_curr = {
                "applied_projects":applied_projects,
                "disable_next_page":disable_next_page,
                "init_page_num":int(request.args.get("page"))
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("student_project_applications.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Öğrenci Proje Başvuruları öğrencileri görüntülerken yapılan ajaxa call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/get_project_application_students',methods=["GET"])
def get_project_application_students_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Öğrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            project_id = request.args.get("project_id")
            project_id = int(project_id)

            academician = session["user"]
            students = academician.get_project_application_students(project_id)

            #Aynı grupta olan öğrenciler aynı liste içinde olacak şekilde listelerin listesi yapısı oluşturulur
            len_students = len(students)
            i=0
            grouped_students = []
            checked_student_dict = {}

            for i in range(len_students):
                k = i+1
                if not checked_student_dict.get(students[i][0]):
                    #Arkadaşı var ise
                    if students[i][3]:

                        for k in range(len_students):
                            #Öğrenciler grup arkadaşı ise
                            if (students[i][0] == students[k][3]):
                                checked_student_dict[students[k][0]] = True
                                grouped_students.append( [students[i], students[k]] )

                    else:
                        grouped_students.append([students[i]])


            grouped_students = json.dumps(grouped_students)

            return grouped_students



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Öğrenci Proje Başvuruları öğrencileri görüntülerken yapılan ajaxa call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/reject_project_application',methods=["GET"])
def reject_project_application_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_3:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Öğrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            student_no = request.args.get("student_no")

            academician = session["user"]

            success = academician.reject_student_project_application(student_no)

            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Öğrenci Proje Başvuruları öğrencileri görüntülerken yapılan ajaxa call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/confirm_project_application',methods=["GET"])
def confirm_project_application_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_3:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Öğrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            student_no = request.args.get("student_no")
            project_id = request.args.get("project_id")
            project_id = int(project_id)

            academician = session["user"]

            response_func = academician.set_student_project(student_no, project_id)

            response = {
            "response":response_func
            }


            return json.dumps(response)



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Arkadaşı Ekle
#Sorumlu kişi: Çetin Tekin
@app.route('/project/send_friend_request',methods=["GET"])
def send_friend_request_handler():
    if request.method == "GET":

        #Surec acik degil ise
        if not PROCESS_1:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            user = session["user"]
            friend_student_no = request.args.get("ogr_list")

            student = session["user"]

            response = None

            students = student.get_all_students()

            #Gonderenin arkadasi var mi?
            friend_exist = student.check_friend()

            if friend_exist:
                response = "you_friend_exist"

                template_values_curr = {
                    "response":response,
                    "students":students
                }


                template_values_index = {
                        "user_type":session["user_type"],
                        "PROCESS_1":PROCESS_1,
                        "PROCESS_2":PROCESS_2,
                        "PROCESS_3":PROCESS_3,
                        "PROCESS_4":PROCESS_4,
                        "PROCESS_5":PROCESS_5,
                        "PROCESS_6":PROCESS_6,
                        "PROCESS_7":PROCESS_7
                }


                return render_template("send_friend_request.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


            #Form gonderildi, arkadaşlık talebi yollandi
            if friend_student_no:
                answer = student.send_friend_request(friend_student_no)
                if answer:
                    response = answer
                else:
                    response = "success"


            template_values_curr = {
                "response":response,
                "students":students
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("send_friend_request.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gelen Arkadaş İstekleri
#Sorumlu kişi: Çetin Tekin
@app.route('/project/my_received_requests',methods=["GET"])
def my_received_requests_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            page_offset = int(request.args.get("page"))
            student = session["user"]
            sender_students = student.get_friend_request_senders(page_offset)



            disable_next_page = False

            #Ogrenci varsa
            if sender_students:

                num_of_students = len(sender_students)
                if num_of_students < 11:
                    disable_next_page = True


                else:
                    #Son eleman silinir
                    sender_students = sender_students[:-1]




            template_values_curr = {
                "sender_students":sender_students,
                "disable_next_page":disable_next_page,
                "init_page_num":int(request.args.get("page"))
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }



            return render_template("my_received_requests.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))






#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gelen Arkadaşlık İstekleri reddetme islemi ajax call
#Sorumlu kişi: Çetin Tekin
@app.route('/project/reject_friend_request',methods=["GET"])
def reject_friend_request_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            student = session["user"]

            student_no=request.args.get("student_no")

            success = student.reject_friend_request(student_no)
            success = {"success":success}
            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gelen Arkadaşlık İstekleri onaylama islemi ajax call
#Sorumlu kişi: Çetin Tekin
@app.route('/project/confirm_friend_request',methods=["GET"])
def confirm_friend_request_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            student = session["user"]

            student_no=request.args.get("student_no")

            answer = student.confirm_friend_request(student_no)
            response = {"answer":answer}
            response = json.dumps(response)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gönderilen Arkadaş İstekleri
#Sorumlu kişi: Çetin Tekin
@app.route('/project/my_sent_requests',methods=["GET"])
def my_sent_requests_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            page_offset = int(request.args.get("page"))
            student = session["user"]
            receiver_students = student.get_friend_request_receivers(page_offset)



            disable_next_page = False

            #Ogrenci varsa
            if receiver_students:

                num_of_students = len(receiver_students)
                if num_of_students < 11:
                    disable_next_page = True


                else:
                    #Son eleman silinir
                    receiver_students = sender_students[:-1]




            template_values_curr = {
                "receiver_students":receiver_students,
                "disable_next_page":disable_next_page,
                "init_page_num":int(request.args.get("page"))
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }



            return render_template("my_sent_requests.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gönderilen Arkadaşlık İstekleri istek iptali islemi ajax call
#Sorumlu kişi: Çetin Tekin
@app.route('/project/cancel_friend_request',methods=["GET"])
def cancel_friend_request_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            student = session["user"]

            student_no=request.args.get("student_no")

            answer = student.cancel_friend_request(student_no)
            response = {"answer":answer}
            response = json.dumps(response)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Arkadaşım
#Sorumlu kişi: Çetin Tekin
@app.route('/project/my_friend',methods=["GET"])
def my_friend_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            user = session["user"]
            student_info = user.get_friend()

            template_values_curr = {
                "student_info":student_info,
                "PROCESS_1":PROCESS_1,
                "PROCESS_7":PROCESS_7
            }

            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }



            return render_template("my_friend.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Gönderilen Arkadaşlık İstekleri istek iptali islemi ajax call
#Sorumlu kişi: Çetin Tekin
@app.route('/project/delete_friend',methods=["GET"])
def delete_friend_request_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not (PROCESS_1 or PROCESS_7):
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            student = session["user"]


            answer = student.delete_friend()
            response = {"answer":answer}
            response = json.dumps(response)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Form-2 Onay Durumu
#Sorumlu kişi: Çetin Tekin
@app.route('/project/form2_status',methods=["GET"])
def form2_status_handler():
    if request.method == "GET":


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))



            user = session["user"]
            project = user.get_project()
            status = None
            council_decision = None

            #Proje var ise
            if project:
                status = project.form2_status
                council_decision = project.council_decision

            template_values_curr = {
                "status":status,
                "council_decision":council_decision
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("form2_status.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Onay Bekleyen Form-2
#Sorumlu kişi: Çetin Tekin
@app.route('/project/form2_pending_projects',methods=["GET"])
def form2_pending_projects_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_5:
            return redirect(url_for("greeting"))

        #Giris yapildi mi?
        if session.get("logged_in"):


            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))



            page_offset = int(request.args.get("page"))

            #Mevcut sessiondan akademisyen nesnesi cekiliyor.
            academician = session["user"]

            projects = academician.get_form2_pending_projects(page_offset)
            disable_next_page = False

            #Proje önerisi varsa
            if projects:

                num_of_projects = len(projects)
                if num_of_projects < 11:
                    disable_next_page = True


                else:
                    #Son eleman silinir
                    projects = projects[:-1]





            #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7

            }


            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                    "projects":projects,
                    "disable_next_page":disable_next_page,
                    "init_page_num":int(request.args.get("page"))

            }

            return render_template("form2_pending_projects.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )





        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Onay Bekleyen Form-2, proje silme işlemi için AJAX call aracılığı ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/reject_form2',methods=["GET"])
def reject_form2_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_5:
            return redirect(url_for("greeting"))

        #Giris yapildi mi?
        if session.get("logged_in"):

            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            project_id = request.args.get("project_id")
            project_id = int(project_id)

            academician  = session["user"]

            success = academician.reject_form2(project_id)

            success = {
            "success":success
            }

            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Onay Bekleyen Form-2, proje silme işlemi için AJAX call aracılığı ile
#Sorumlu kişi: Çetin Tekin
@app.route('/project/confirm_form2',methods=["GET"])
def confirm_form2_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_5:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))


            project_id = request.args.get("project_id")
            project_id = int(project_id)

            academician  = session["user"]

            success = academician.confirm_form2(project_id)

            success = {
            "success":success
            }

            response = json.dumps(success)

            return response



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Proje Raporu Gönder
#Sorumlu kişi: Çetin Tekin
@app.route('/project/send_project_report',methods=["GET","POST"])
def send_project_report_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_7:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            template_values_curr = {
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("send_project_report.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))


    #post method
    else:

        #Surec acik mi?
        if not PROCESS_7:
            return redirect(url_for("greeting"))


        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))


            report_type = request.form['report_type_select']
            user = session["user"]
            f = request.files['file_to_send']
            report_blob_data = f.read()

            response = user.add_report(report_type, report_blob_data)

            if response:
                success = "true"

            template_values_curr = {
                "success":success
            }



            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }



            return render_template("send_project_report.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Onay Bekleyen Form-2
#Sorumlu kişi: Çetin Tekin
@app.route('/project/sent_project_reports',methods=["GET"])
def sent_project_reports_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("logged_in"):


            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))




            #Mevcut sessiondan akademisyen nesnesi cekiliyor.
            student = session["user"]

            project_report_situations = student.get_report_situations()



            #NOT: Bu dictionay'de index html icin render edilmesi gereken degiskenler aktarilir, index.html'den kalitim aldigimiz icin
            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7

            }


            #Bu dictionary'de bu sayfada islemler sonucu olusturulan degiskenler aktarilir
            template_values_curr = {
                    "project_report_situations":project_report_situations
            }

            return render_template("sent_project_reports.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )





        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Akademisyen Onaylı Form-2'leri İndir
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/download_form2',methods=["GET"])
def admin_download_form2_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            data = None

            try:
                cursor.execute('SELECT project_id,project_name,form2 FROM Project WHERE form2_status=%s', ("council_pending",))
                all_projects=cursor.fetchall()

                #Akademisyen onayindan gecmis form-2ler zipleniyor
                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    for project in all_projects:
                        data = zipfile.ZipInfo(str(project[0])+"_"+project[1]+".pdf")
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, project[2])
                memory_file.seek(0)
                return send_file(memory_file, attachment_filename='allForm2.zip', as_attachment=True)

            finally:
                connection.close()

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))





#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Rapor İndir
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/download_report',methods=["GET"])
def admin_download_report_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()
            report_type = request.args.get("report_type")

            data = None

            try:

                exist_word = report_type+"_exist"

                cursor.execute(
                sql.SQL("SELECT project_id,project_name,{} FROM Project WHERE {}=%s").format(
                *map(sql.Identifier, (report_type, exist_word))), ("true",))

                all_projects=cursor.fetchall()

                #Akademisyen onayindan gecmis form-2ler zipleniyor
                memory_file = BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    for project in all_projects:
                        data = zipfile.ZipInfo(str(project[0])+"_"+project[1]+".pdf")
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, project[2])
                memory_file.seek(0)
                return send_file(memory_file, attachment_filename=report_type+'.zip', as_attachment=True)

            finally:
                connection.close()

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Form-2 Kurul Onayı
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/form2_council_decision',methods=["GET","POST"])
def form2_council_decision_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()


            try:

                cursor.execute(
                'SELECT student_no,name,sname FROM Student,Project WHERE Project.project_id=Student.project_id AND \
                form2_status=%s', ("council_pending",))

                data = cursor.fetchall()

                template_values_curr = {
                "students":data
                }

                return render_template("admin_form2_council_decision.html",template_values_curr=json.dumps(template_values_curr) )

            finally:
                connection.close()



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))


    #method post
    else:

        #Giris yapildi mi?
        if session.get("admin_logged_in"):
            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            student_no = request.form['ogr_list']
            council_decision = request.form['council_decision']
            op_type = request.form['op_type']

            try:

                if op_type == "onay":

                    cursor.execute(
                    'UPDATE Project SET form2_status=%s,form2_council_decision=%s WHERE project_id IN(\
                    SELECT project_id \
                    FROM Student \
                    WHERE student_no=%s)', ("council_confirmed",council_decision,student_no))


                elif op_type == "red":

                    cursor.execute(
                    'UPDATE Project SET form2_status=%s,form2_council_decision=%s WHERE project_id IN(\
                    SELECT project_id \
                    FROM Student \
                    WHERE student_no=%s)', ("council_rejected",council_decision,student_no))



                cursor.execute(
                'SELECT student_no,name,sname FROM Student,Project WHERE Project.project_id=Student.project_id AND \
                form2_status=%s', ("council_pending",))

                data = cursor.fetchall()


                template_values_curr = {
                "response":"success",
                "students":data
                }


                return render_template("admin_form2_council_decision.html",template_values_curr=json.dumps(template_values_curr) )

            finally:
                connection.commit()
                connection.close()

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje İşlemleri/Öğrenci Raporu İndir
#Sorumlu kişi: Çetin Tekin
@app.route('/project/get_student_report',methods=["GET"])
def get_student_report_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("logged_in"):

            #Ogrenciler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "student":
                return redirect(url_for("greeting"))



            academician = session["user"]

            #Raporu olan projeler cekiliyor
            projects = academician.get_all_projects_with_report()

            template_values_curr = {
                "projects":projects,
            }


            template_values_index = {
                "user_type":session["user_type"],
                "PROCESS_1":PROCESS_1,
                "PROCESS_2":PROCESS_2,
                "PROCESS_3":PROCESS_3,
                "PROCESS_4":PROCESS_4,
                "PROCESS_5":PROCESS_5,
                "PROCESS_6":PROCESS_6,
                "PROCESS_7":PROCESS_7
            }




            return render_template("get_student_report.html",template_values=template_values_index,template_values_curr=json.dumps(template_values_curr) )



        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin Paneli/Sistemi Sıfırla
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/system_reset',methods=["GET"])
def system_reset_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):
            return render_template("admin_system_reset.html")

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin Paneli/Sistemi Sıfırla ajax call
#Sorumlu kişi: Çetin Tekin
@app.route('/system_reset',methods=["GET"])
def system_reset_handler_2():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            response = {
            "success":False
            }

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            try:
                #Base proje bilgileri guncelleniyor
                cursor.execute('UPDATE Project \
                SET fullness=%s \
                WHERE capacity IS NOT NULL', (0,))

                #Base projeler disinda tum projeler siliniyor
                cursor.execute('DELETE FROM Project \
                WHERE capacity IS NULL;')

                #Ogrenci tablosunda devam karari alanlar icin
                cursor.execute('UPDATE Student \
                SET project_id=%s,apply_project_status=%s,grade=%s \
                WHERE continuation IS NOT NULL', (None,"pending",None))

                #Ogrenci tablosunda devam karari almayanlar icin
                cursor.execute('UPDATE Student \
                SET project_id=%s,apply_project_status=%s,apply_project_id=%s,grade=%s \
                WHERE continuation IS NULL', (None,None,None,None))

                response["success"] = True


            finally:
                connection.commit()
                connection.close()
                return json.dumps(response)

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Kayıt Onayı Bekleyen Öğrenciler
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/register_pending_students',methods=["GET"])
def register_pending_students_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            page_offset = int(request.args.get("page"))
            query_offset = (page_offset-1)*10


            try:

                cursor.execute(
                'SELECT student_no FROM Student WHERE active=%s OFFSET %s LIMIT 11', ("false",query_offset))

                data = cursor.fetchall()

                disable_next_page = False

                if data:
                    num_of_students = len(data)
                    if num_of_students < 11:
                        disable_next_page = True


                    else:
                        #Son eleman silinir
                        students = students[:-1]


                template_values_curr = {
                "students":data,
                "disable_next_page":disable_next_page,
                "init_page_num":int(request.args.get("page"))
                }

                return render_template("admin_register_pending_students.html",template_values_curr=json.dumps(template_values_curr) )

            finally:
                connection.close()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Kayıt Onayı Bekleyen Öğrenciler AJAX call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/confirm_registration',methods=["GET"])
def confirm_registration_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            op_type = request.args.get("op_type")
            std_no = request.args.get("student_no")

            admin = Admin()

            success = "false"

            #SMTP server giris
            server = smtplib.SMTP("smtp.gmail.com:587")
            server.ehlo()
            server.starttls()
            server.login(session["admin_username"], session["admin_password"])


            try:

                #Tum ogrencilerin hesabi aktiflestirilir
                if op_type == "all":
                    cursor.execute(
                    'SELECT student_no FROM Student WHERE active=%s', ("false",))

                    students = cursor.fetchall()

                #Bir ogrenci secilip hesabi aktiflestiriliyorsa
                elif op_type == "single":
                    students = [[std_no]]


                for std in students:
                    student_no = std[0]

                    generated_password = admin.generate_random_password()
                    password_hash = generate_password_hash(generated_password)

                    email = "l11"

                    #Ogrenci numarasindan email generate ediliyor
                    if len(student_no) == 8:
                        email += student_no[:2]


                    elif len(student_no) == 7:
                        email += "0"
                        email += student_no[:1]

                    email += student_no[-3:]
                    email += "@std.yildiz.edu.tr"


                    #Kullaniciya sifresini mail ile  gonderme islemi
                    body ="Merhaba " + student_no + ",\n\n" + generated_password + " sifresi ile sisteme giris yapabilirsiniz.\n\nYTU Proje Takip Sistemi Ekibi"
                    message="Subject: {}\n\n{}".format("YTU Proje Takip Sistemi Hesap Sifreniz", body)
                    server.sendmail(session["admin_username"], email, message)

                    #Kullanici hesabi aktiflestirme islemi
                    cursor.execute(
                    'UPDATE Student SET active=%s, password=%s WHERE student_no=%s AND active=%s', ("true", password_hash, student_no, "false"))


                success = "true"
            except Exception as e:
                return str(e)

            finally:
                connection.commit()
                connection.close()
                server.quit()

                response = {"success":success}
                return json.dumps(response)

        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))




#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Admin/Kayıt Onayı Bekleyen Öğrenciler AJAX call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/admin/reject_registration',methods=["GET"])
def reject_registration_handler():
    if request.method == "GET":

        #Giris yapildi mi?
        if session.get("admin_logged_in"):

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            student_no = request.args.get("student_no")

            try:

                #Kullanici hesabi basvurusu silme islemi
                cursor.execute(
                'DELETE FROM Student WHERE student_no=%s AND active=%s', (student_no,"false"))

                response = {"success":"success"}
                return json.dumps(response)


            except Exception as e:
                return str(e)

            finally:
                connection.commit()
                connection.close()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("admin_login_handle"))



#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: Proje/Devam Karari
#Sorumlu kişi: Çetin Tekin
@app.route('/grade/confirm_continuation',methods=["GET"])
def confirm_continuation_handler():
    if request.method == "GET":

        #Surec acik mi?
        if not PROCESS_8:
            return redirect(url_for("greeting"))

        #Giris yapildi mi?
        if session.get("logged_in"):

            #Akademisyenler sayfaya girmeye calisirsa ana sayfaya atiliyor
            if session["user_type"] == "academician":
                return redirect(url_for("greeting"))

            user = session["user"]
            user.confirm_continuation()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))


#Request Handler Bilgileri
#-----------*-------------
#Uygulama içerisinde ulaşmak için: /edit_info AJAX call ile
#Sorumlu kişi: Çetin Tekin
@app.route('/edit_info',methods=["POST"])
def edit_info_handler():
    if request.method == "POST":

        #Giris yapildi mi?
        if session.get("logged_in"):

            modal_name = request.json['modal_name']
            modal_sname = request.json['modal_sname']
            modal_pass = request.json['modal_pass']


            modal_pass = generate_password_hash(modal_pass)

            user_type = session["user_type"]
            user = session["user"]

            connection = psycopg2.connect(DATABASE_URL, sslmode='allow')
            cursor = connection.cursor()

            try:


                if user_type == "student":
                    cursor.execute('UPDATE Student \
                    SET name=%s,sname=%s,password=%s,first_timer=%s \
                    WHERE student_no=%s',(modal_name,modal_sname,modal_pass,"false",user.student_no))

                    user.name = modal_name
                    user.sname = modal_sname


                elif user_type == "academician":
                    cursor.execute('UPDATE Academician \
                    SET password=%s,first_timer=%s \
                    WHERE username=%s',(modal_pass,"false",user.username))




                user.first_timer = "false"

                session.pop("user", None)

                session["user"] = user

                success = {
                    "success":"success"
                }

                response = json.dumps(success)

                return response


            finally:
                connection.commit()
                connection.close()


        #Giris yapilmadiysa giris sayfasina yonlendirilir.
        return redirect(url_for("login_handle"))



if __name__ == '__main__':
   app.run(debug = True)
