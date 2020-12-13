from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

from threading import Thread
from time import sleep
from datetime import datetime, time

import csv
import requests
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "pLoKmIjNuHbYgVtFcRdXeSzWaQ"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id_ = db.Column("id", db.Integer, primary_key=True)
    uname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    psw = db.Column(db.Text, nullable=False)
    
    gender = db.Column(db.String(6), default=None)
    height = db.Column(db.Integer, default=None)
    weight = db.Column(db.Integer, default=None)
    age = db.Column(db.Integer, default=None)
    
    day_calories_eaten = db.Column(db.Integer, default=0)
    day_calories_burned = db.Column(db.Integer, default=0)
    week_calories_eaten = db.Column(db.Integer, default=0)
    week_calories_burned = db.Column(db.Integer, default=0)
    month_calories_eaten = db.Column(db.Integer, default=0)
    month_calories_burned = db.Column(db.Integer, default=0)
    year_calories_eaten = db.Column(db.Integer, default=0)
    year_calories_burned = db.Column(db.Integer, default=0)
    
    a = db.Column(db.Integer, default=0) #RMR
    b = db.Column(db.Integer, default=0)
    c = db.Column(db.Integer, default=0)
    d = db.Column(db.Integer, default=0)
    e = db.Column(db.Integer, default=0)
    f = db.Column(db.Integer, default=0)
    g = db.Column(db.Integer, default=0)
    h = db.Column(db.Integer, default=0)
    i = db.Column(db.Integer, default=0)
    
    j = db.Column(db.Text, default="") #Excercise history
    k = db.Column(db.Text, default="")
    l = db.Column(db.Text, default="")
    m = db.Column(db.Text, default="")
    n = db.Column(db.Text, default="")
    o = db.Column(db.Text, default="")
    p = db.Column(db.Text, default="")
    q = db.Column(db.Text, default="")
    r = db.Column(db.Text, default="")

    def __repr__(self):
        return "{0}: {1} at {2}".format(self.id_, self.uname, self.email)

@app.before_first_request
def init_db():
  db.create_all()

@app.before_first_request
def update_activity_mets():
  global activity_mets
  activity_mets = get_activity_mets()

GETPOST = ["GET", "POST"]
activity_mets = []

def get_activity_mets():
  with open("activity_mets.csv") as file:
    reader = csv.reader(file, delimiter="|", quotechar=">")
    activity_mets = []
    for x, sport in enumerate(reader):
      new_sport = [sport[0].strip(), sport[1].strip().title(), float(sport[2]), x]
      activity_mets.append(new_sport)
    return activity_mets

def get_mets(activity):
  print(f"Getting mets for {activity}")
  for activity_details in activity_mets:
    if activity_details[1] == activity:
      print(f"Mets for {activity} is {activity_details[2]}")
      return activity_details[2]
  print("Mets not found :(")
  return -1.0

def get_calories(activity, weight, minutes):
  print(f"Getting calories for {activity} for {minutes} with person weighing {weight}")
  return (get_mets(activity) * 3.5 * weight * minutes) / 200

def calcRMR(gender, weight, height, age):
  if gender == "male":
    return 10 * weight + 6.25 * height - 5 * age + 5
  elif gender == "female":
    return 10 * weight + 6.25 * height - 5 * age - 161
  elif gender == "other":
    return 10 * weight + 6.25 * height - 5 * age - 78

def login_db(uname, psw):
  match = User.query.filter_by(uname=uname).first()
  if match and psw == match.psw:
    session["logged_in"] = True
    session["uname"] = match.uname
    session["email"] = match.email
    flash(f"SSuccessfully logged in as {match.uname}!")
    return True
  flash("DIncorrect Username or Password!")
  return False

def register_db(uname, email, psw):
  new_user = User(uname=uname, email=email, psw=psw)
  db.session.add(new_user)
  db.session.commit()
  flash(f"SSuccessfully Registered as {new_user.uname}!")

def day_reset():
  while True:
    now = datetime.now().time()
    oneoclock = time(hour=1, minute=0, second=0)
    oneoclockplusone = time(hour=1, minute=1, second=0)
    if oneoclock < now < oneoclockplusone:
      for user in User.query.all():
        user.day_calories_eaten = 0
        user.day_calories_burned = 0
    sleep(20000)
    

def week_reset():
  while True:
    now = datetime.now().time()
    oneoclock = time(hour=1, minute=0, second=0)
    oneoclockplusone = time(hour=1, minute=1, second=0)
    if oneoclock < now < oneoclockplusone and datetime.now().weekday() == 6:
      for user in User.query.all():
        user.day_calories_eaten = 0
        user.day_calories_burned = 0
    sleep(20000)

def month_reset():
  while True:
    now = datetime.now().time()
    oneoclock = time(hour=1, minute=0, second=0)
    oneoclockplusone = time(hour=1, minute=1, second=0)
    if oneoclock < now < oneoclockplusone and datetime.now().weekday() == 6:
      for user in User.query.all():
        user.day_calories_eaten = 0
        user.day_calories_burned = 0
    sleep(20000)

@app.route("/")
def index():
  if session.get("logged_in"):
    match = User.query.filter_by(uname=session.get("uname")).first()
    return render_template("index.html", uname=session.get("uname"), activity_mets=activity_mets, history=match.j)
  else:
    return render_template("index.html", uname=session.get("uname"), activity_mets=activity_mets, history=None)

@app.route("/login", methods=GETPOST)
def login():
  if session.get("logged_in"):
    flash("DYou are already logged in!")
    return redirect(url_for("index"))
  if request.method == "POST":
    uname = request.form.get("uname")
    psw = request.form.get("psw")
    remember = request.form.get("remember")
    login_db(uname, psw)
    return redirect(url_for("index"))
  return render_template("login.html", uname=session.get("uname"))

@app.route("/register", methods=GETPOST)
def register():
  if session.get("logged_in"):
    flash("DYou are already logged in!")
    return redirect(url_for("index"))
  if request.method == "POST":
    uname = request.form.get("uname")
    email = request.form.get("email")
    psw = request.form.get("psw")
    register_db(uname, email, psw)
    return redirect(url_for("login"))
  return render_template("register.html", uname=session.get("uname"))

@app.route("/logout", methods=GETPOST)
def logout():
  uname = session.get("uname")
  session.clear()
  flash(f"SSuccessfully Logged Out from {uname}!")
  return redirect(url_for("login"))

@app.route("/myaccount", methods=GETPOST)
def my_account():
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  match = User.query.filter_by(uname=session.get("uname")).first()
  if request.method == "POST":
    gender = request.form.get("gender")
    height = int(request.form.get("height"))
    weight = int(request.form.get("weight"))
    age = int(request.form.get("age"))
    npsw = request.form.get("npsw")
    opsw = request.form.get("opsw")
    if npsw and opsw:
      if opsw == match.psw:
        match.psw = npsw
        db.session.commit()
        flash("SPassword Successfully Changed!")
      else:
        flash("DIncorrect Old Password! Please Try Again or use <a href='/forgotpassword'>Forgot Password</a> to reset your password.")
    else:
      if gender:
        match.gender = gender
      if height:
        if request.form.get("units") == "on":
          height *= 2.54
        match.height = int(height)
      if weight:
        if request.form.get("units") == "on":
          weight /= 2.20462262
        match.weight = int(weight) 
      if age:
        match.age = int(age)
      match.a = calcRMR(gender, weight, height, age)
      db.session.commit()
      flash("SSuccessfully Updated Biometric Data!")
      return redirect(url_for("my_account"))
  return render_template("myaccount.html", 
                         uname=session.get("uname"), 
                         email=match.email, 
                         psw=match.psw, 
                         gender=match.gender, 
                         height=match.height, 
                         weight=match.weight, 
                         age=match.age)

@app.route("/nutrition", methods=GETPOST)
def nutrition():
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  if request.method == "POST":
    search = request.form.get("search")
    smass = request.form.get("smass")
    upc = request.form.get("upc")
    umass = request.form.get("umass")
    if search and smass:
      response = requests.get(f"https://api.edamam.com/api/food-database/v2/parser?ingr={search.replace(' ', '%20')}&app_id=88a43868&app_key=e512bec8d5a4570675eec4b47858e83e").json()["hints"][1]["food"]
      label = response["label"]
      cals = (response["nutrients"]["ENERC_KCAL"]) * (float(smass) / 100)
      session["label"] = label
      session["food_cals"] = cals
      flash(f"Sadding {cals} calories from {label}, orO")
    elif upc and umass:
      response = requests.get(f"https://api.edamam.com/api/food-database/v2/parser?upc={upc}&app_id=88a43868&app_key=e512bec8d5a4570675eec4b47858e83e").json()["hints"][0]["food"]
      label = response["label"]
      cals = (response["nutrients"]["ENERC_KCAL"]) * (float(umass) / 100)
      match = User.query.filter_by(uname=session.get("uname")).first()
      match.day_calories_eaten += cals
      match.week_calories_eaten += cals
      match.month_calories_eaten += cals
      match.year_calories_eaten += cals
      db.session.commit()
      flash(f"SSuccessfully added {cals} calories from {label}!")
    else:
      flash("DPlease fill out all form fields!")
    return redirect(url_for("nutrition"))
  match = User.query.filter_by(uname=session.get("uname")).first()
  return render_template("nutrition.html", 
                         uname=session.get("uname"), 
                         day_calories_eaten=match.day_calories_eaten, 
                         week_calories_eaten=match.week_calories_eaten, 
                         month_calories_eaten=match.month_calories_eaten, 
                         life_calories_eaten=match.year_calories_eaten)


@app.route("/add_nutrition")
def add_nutrition():
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  if session.get("food_cals"):
    match = User.query.filter_by(uname=session.get("uname")).first()
    if not match.gender or not match.weight or not match.height or not match.age:
      flash("DPlease set your gender, weight, height, and age first!")
      return redirect(url_for("my_account"))
    flash(f"SSuccessfully added {session.get('food_cals')} calories from {session.get('label')}!")
    match.day_calories_eaten += session["food_cals"]
    match.week_calories_eaten += session["food_cals"]
    match.month_calories_eaten += session["food_cals"]
    match.year_calories_eaten += session["food_cals"]
    db.session.commit()
    del session["label"]
    del session["food_cals"]
  else:
    flash("DPlease Choose a Food Item first!")
  return redirect(url_for("nutrition"))

@app.route("/remove_nutrition")
def remove_nutrition():
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  del session["food_cals"]
  del session["label"]
  return redirect(url_for("nutrition"))

@app.route("/activity", methods=GETPOST)
def activity():
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  match = User.query.filter_by(uname=session.get("uname")).first()
  return render_template("activity.html", uname=session.get("uname"), life_calories_burned=match.year_calories_burned, life_calories_eaten=match.year_calories_eaten, rmr=match.a, age=match.age, weight=match.age, activity_mets=activity_mets)

@app.route("/do_activity/<int:id>/<int:mins>")
def do_activity(id, mins):
  if not session.get("logged_in"):
    flash("DYou muct log in first to access this page!")
    return redirect(url_for("login"))
  match = User.query.filter_by(uname=session.get("uname")).first()
  if not match.gender or not match.weight or not match.height or not match.age:
      flash("DPlease set your gender, weight, height, and age first!")
      return redirect(url_for("my_account"))
  activity = activity_mets[id]
  cals = get_calories(activity[1], match.weight, mins)
  match.day_calories_burned += cals
  match.week_calories_burned += cals
  match.month_calories_burned += cals
  match.year_calories_burned += cals
  match.j += str(activity[3]) + "|" + str(mins) + "\n"
  db.session.commit()
  flash(f"SSuccessfully completed {activity}!")
  return redirect(url_for("index"))


if __name__ == "__main__":
  day_reset_thread = Thread(target=day_reset)
  week_reset_thread = Thread(target=week_reset)
  month_reset_thread = Thread(target=month_reset)
  day_reset_thread.start()
  week_reset_thread.start()
  month_reset_thread.start()
  app.run(debug=True)