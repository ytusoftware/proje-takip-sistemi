from flask import Flask, redirect, url_for, request, render_template, send_from_directory, session
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
        return render_template("index.html")

    return redirect(url_for("login_handle"))




#KULLANICI LOGIN HANDLE
@app.route('/login', methods = ["GET","POST"])
def login_handle():
    if request.method == "GET":
        session["login_failure"] = False
        return render_template("login.html",login_failure=session["login_failure"])

    else:
        #username_student_no can be username or student_no
        username_student_no = request.form['username']
        password = request.form['password']
        user_type = request.form['tipsec']

        if user_type == "student":
            user = Student.find_by_student_no(username_student_no)

        else:
            user = Academician.find_by_username(username_student_no)



        if user and check_password_hash(user.password, password):
            #Mevcut kullanici objesi session'da kaydediliyor
            session["user"] = user
            session["logged_in"] = True

            return redirect(url_for("greeting"))


        session["login_failure"] = True
        return render_template("login.html", login_failure=session["login_failure"])




#LOGOUT HANDLE
@app.route('/logout')
def logout_handle():
    session.pop("logged_in", None)
    session.pop("login_failure", None)
    session.pop("user", None)
    return redirect(url_for("greeting"))




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


            try:

                admin = Admin()

                #Turkce karakter kontrolu. Mail gonderirken turkce karakter sikinti oluyor.
                if not (all(ord(char) < 128 for char in student_no_username)):

                    template_values={
                    'message':"error",
                    'error':"Kullanici adinda turkce karakter bulunmamali!"
                    }

                    return render_template("admin_index.html",template_values=json.dumps(template_values))



                #Veri tabanina yazma islemi
                admin.write_db(user_type, student_no_username, name, sname)



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


                template_values = {
                'message':"success"
                }


                return render_template("admin_index.html",template_values=json.dumps(template_values))

            except Exception as e:
                student_no_username = request.form["student_no_username"]

                error_message = "Hatanin sebebi " + student_no_username + " kullanici adli/ogrenci nolu kullanicinin veri tabaninda bulunmasi olabilir."


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




'''
#DOSYA UPLOAD ICIN TASLAK KOD
@app.route('/uploader',methods = ['POST', 'GET'])
def upload_handle():
    if request.method == 'POST':
        f = request.files['filem']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploads_page_display'))
'''


'''
@app.route('/myuploads', methods = ['POST','GET'])
def uploads_page_display():


    #Getting list of all files in the uploads
    all_files = [f for f in listdir(app.config['UPLOAD_FOLDER']) if isfile(join(app.config['UPLOAD_FOLDER'], f))]

    return render_template("uploads_display.html",all_files=all_files)
'''

'''
#DOSYA INDIRME ISLEMI ICIN
@app.route('/download')
def download_file():
        file = request.args.get("filename")
        return send_from_directory(app.config['UPLOAD_FOLDER'],file, as_attachment=True)

'''


if __name__ == '__main__':
   app.run(debug = True)
