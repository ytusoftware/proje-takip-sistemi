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


        #Mevcut kullanici objesi session'da kaydediliyor
        session["user"] = user


        if user and check_password_hash(user.password, password):
            session["logged_in"] = True
            return redirect(url_for("greeting"))  # user token?


        session["login_failure"] = True
        return render_template("login.html", login_failure=session["login_failure"])




#LOGOUT HANDLE
@app.route('/logout')
def logout_handle():
    session.pop("logged_in", None)
    session.pop("login_failure", None)
    session.pop("user", None)
    return redirect(url_for("greeting"))


#DOSYA UPLOAD ICIN TASLAK KOD
@app.route('/uploader',methods = ['POST', 'GET'])
def upload_handle():
    if request.method == 'POST':
        f = request.files['filem']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploads_page_display'))




@app.route('/myuploads', methods = ['POST','GET'])
def uploads_page_display():


    #Getting list of all files in the uploads
    all_files = [f for f in listdir(app.config['UPLOAD_FOLDER']) if isfile(join(app.config['UPLOAD_FOLDER'], f))]

    return render_template("uploads_display.html",all_files=all_files)



#DOSYA INDIRME ISLEMI ICIN
@app.route('/download')
def download_file():
        file = request.args.get("filename")
        return send_from_directory(app.config['UPLOAD_FOLDER'],file, as_attachment=True)




if __name__ == '__main__':
   app.run(debug = True)
