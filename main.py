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

#Session token set ediliyor
#app.config['SECRET_KEY'] = os.urandom(16)



#KARSILAMA SAYFASI
@app.route('/')
def greeting():
    #return render_template("index.html")
    if session.get("logged_in"):
        return render_template("index.html", username=session["username"])

    return redirect(url_for("login_handle"))



#KULLANICI KAYDI ISLEMLERI ICIN
@app.route('/register', methods = ["POST", "GET"])
def register_handle():
    if request.method == "GET":
        return render_template("register.html",user_exist_flag=0)

    else:
        username = request.form['username']
        password = request.form['password']

        try:
            User(username, generate_password_hash(password)).save_to_db()
        except Exception as e:
            return render_template("register.html",user_exist_flag=1)


    session["logged_in"] = True
    session["username"] = request.form['username']

    return redirect(url_for("greeting"))


#KULLANICI LOGIN HANDLE
@app.route('/login', methods = ["GET","POST"])
def login_handle():
    if request.method == "GET":
        return render_template("login.html")

    else:
        username = request.form['username']
        password = request.form['password']
        user = User.find_by_username(username)


    if user and check_password_hash(user.password, password):
        session["logged_in"] = True
        session["username"] = request.form['username']
        return redirect(url_for("greeting"))  # user token?
    return render_template("login.html")



#LOGOUT HANDLE
@app.route('/logout')
def logout_handle():
    session.pop("username", None)
    session.pop("logged_in", None)
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
