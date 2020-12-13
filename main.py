from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

from threading import Thread
from time import sleep
import datetime

import math
import csv
import requests
import json
from random import random
import numpy as np

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
    
    a = db.Column(db.Integer, default=0) # RMR
    b = db.Column(db.Integer, default=0) # Used to adjust calorie calcoulations
    c = db.Column(db.Integer, default=0) # Used to adjust calorie calcoulations
    d = db.Column(db.Integer, default=0) # Used to adjust calorie calcoulations
    e = db.Column(db.Integer, default=0) #Used for machine learning
    f = db.Column(db.Integer, default=0) #Also used for weight history
    g = db.Column(db.Integer, default=0) #used for activity history
    h = db.Column(db.Integer, default=0) #met average neumerator
    i = db.Column(db.Integer, default=0) #met average denominator
    
    j = db.Column(db.Text, default="") # Excercise history
    k = db.Column(db.Text, default="") # Day Reset
    l = db.Column(db.Text, default="") # Week Reset
    m = db.Column(db.Text, default="") # Month Reset
    n = db.Column(db.Text, default="") # Weight history
    o = db.Column(db.Text, default="") # Cal history
    p = db.Column(db.Text, default="") #Used for weight history
    q = db.Column(db.Text, default="") #Activity history
    r = db.Column(db.Text, default="") #Used for activity history

    def __repr__(self):
        return "{0}: {1} at {2}".format(self.id_, self.uname, self.email)

def estimate_coef(x, y): #retrieved from https://www.geeksforgeeks.org/linear-regression-python-implementation/
    # number of observations/points 
    n = np.size(x) 
  
    # mean of x and y vector 
    m_x, m_y = np.mean(x), np.mean(y) 
  
    # calculating cross-deviation and deviation about x 
    SS_xy = np.sum(y*x) - n*m_y*m_x 
    SS_xx = np.sum(x*x) - n*m_x*m_x 
  
    # calculating regression coefficients 
    b_1 = SS_xy / SS_xx 
    b_0 = m_y - b_1*m_x 
  
    return(b_0, b_1) 

@app.before_first_request
def init_db():
  db.create_all()

@app.before_first_request
def update_activity_mets():
  global activity_mets
  activity_mets = get_activity_mets()

@app.before_request
def day_reset():
  if session.get("uname"):
    match = User.query.filter_by(uname=session["uname"]).first()
    now = datetime.datetime.now()
    reset = False
    if not match.k:
      match.k = now.strftime("%m/%d/%Y %H:%M:%S")
    else:
      reset_dt = datetime.datetime.strptime(match.k, "%m/%d/%Y %H:%M:%S")
      while now > reset_dt:
        reset_dt += datetime.timedelta(days=1)
        if not reset:
          match.day_calories_eaten = 0
          match.day_calories_burned = 0
          reset = True
      match.k = reset_dt.strftime("%m/%d/%Y %H:%M:%S")
  db.session.commit()

def learn(user):
  x = user.o.split("|")
  temp = user.n.split("\n")
  temp2 = 0.0
  for i in temp:
    i = i.split("|")
    temp2 = max(i[1], float(temp2))
  y = []
  temp3 = int(temp2)
  k = 0
  for i in range(temp3):
    j = 0
    ct = 0
    total = 0
    while(j < i + 1 and k < temp.length):
      total += float(temp[k][0])
      j = float(temp[k][1])
      ct += 1
      k += 1
    y[i] = total / ct
  newVals = estimate_coef(np.array(x), np.array(y))
  return([newVals, x, y])


@app.before_request
def week_reset():
  if session.get("uname"):
    match = User.query.filter_by(uname=session["uname"]).first()
    now = datetime.datetime.now()
    reset = False
    if not match.l:
      match.l = now.strftime("%m/%d/%Y %H:%M:%S")
    else:
      reset_dt = datetime.datetime.strptime(match.l, "%m/%d/%Y %H:%M:%S")
      while now > reset_dt:
        reset_dt += datetime.timedelta(days=7)
        match.o += str(match.week_calories_eaten - match.week_calories_burned) + "|"
        match.e += 1
        if match.e > 4:
          nv = learn(match)
          match.o = ''
          match.n = ''
          for i in range(math.floor(match.e ** 0.5), nv[1].length):
            match.o += str(nv[1])
            match.n += str(nv[2]) + "|" + str(i - math.floor(match.e ** 0.5)) + "\n"
          match.c -= nv[0][0]
          match.b -= math.e**(1.0 / nv[0][1]) - math.e
        if not reset:
          match.week_calories_eaten = 0
          match.week_calories_burned = 0
          reset = True
          flash("DPlease update your weight now! It has been a week since you last updated your weight.")
      match.l = reset_dt.strftime("%m/%d/%Y %H:%M:%S")
  db.session.commit()

@app.before_request
def month_reset():
  if session.get("uname"):
    match = User.query.filter_by(uname=session["uname"]).first()
    now = datetime.datetime.now()
    reset = False
    if not match.m:
      match.m = now.strftime("%m/%d/%Y %H:%M:%S")
    else:
      reset_dt = datetime.datetime.strptime(match.m, "%m/%d/%Y %H:%M:%S")
      while now > reset_dt:
        reset_dt += datetime.timedelta(days=30)
        if not reset:
          match.month_calories_eaten = 0
          match.month_calories_burned = 0
          reset = True
      match.m = reset_dt.strftime("%m/%d/%Y %H:%M:%S")
  db.session.commit()

GETPOST = ["GET", "POST"]
MS_PER_DAY = 86400000.0
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
  for activity_details in activity_mets:
    if activity_details[1] == activity:
      return activity_details[2]
  return -1.0

def get_calories(activity, rmr, d=0):
  #print(f"Getting calories for {activity} for {minutes} with person weighing {weight}")
  return (get_mets(activity) ** (1 / (d+1)) * float(rmr))

def calcRMR(gender, weight, height, age, b=0, c=0):
  if gender == "male":
    return (66.47 + 13.75 * weight + 5.003 * height - 6.755 * age) * math.log(b + math.e) + c
  elif gender == "female":
    return (655.1 + 9.563 * weight + 1.85 * height - 4.676 * age) * math.log(b + math.e) + c
  else:
    return (10.0 * weight + 6.25 * height - 5.0 * age - 78.0) * math.log(b + math.e) + float(c)

@app.route("/updateRMR")
def updateRMR(t):
  uname = session.get("uname")
  if not uname:
    return redirect(url_for("index"))
  match = User.query.filter_by(uname=uname).first()
  cals_burned = float(t) * match.a / MS_PER_DAY
  match.day_calories_burned += cals_burned
  match.week_calories_burned += cals_burned
  match.month_calories_burned += cals_burned
  match.year_calories_burned += cals_burned
  db.session.commit()

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

@app.route("/")
def index():
  if session.get("logged_in"):
    match = User.query.filter_by(uname=session.get("uname")).first()
    mets = ""
    for i in activity_mets:
      mets += "\n"
      for j in i:
        mets += str(j) + "|"
    return render_template("index.html", 
                         uname=session.get("uname"), 
                         email=match.email, 
                         gender=match.gender, 
                         height=match.height, 
                         weight=match.weight, 
                         age=match.age,
                         history=match.j,
                         activity_mets=mets,
                         day_calories_eaten=match.day_calories_eaten, 
                         week_calories_eaten=match.week_calories_eaten, 
                         month_calories_eaten=match.month_calories_eaten, 
                         life_calories_eaten=match.year_calories_eaten,
                         day_calories_burned=match.day_calories_burned,
                         week_calories_burned=match.week_calories_burned,
                         month_calories_burned=match.month_calories_burned,
                         life_calories_burned=match.year_calories_burned)
  else:
    return render_template("index.html")

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
    if User.query.filter_by(uname=uname).first():
      flash("DUsername is taken!")
      return redirect(url_for("register"))
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
    height = request.form.get("height")
    weight = request.form.get("weight")
    age = request.form.get("age")
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
        height = int(height)
        if request.form.get("units") == "on":
          height *= 2.54
        match.height = int(height)
      if weight:
        weight = int(weight)
        if request.form.get("units") == "on":
          weight /= 2.20462262
          if match.f != 0:
            match.n += str(weight) + "|" + match.p + "\n"
            match.p = str((float(datetime.datetime.now().toordinal()) - float(match.f)) / (MS_PER_DAY * 7.0 / 1000.0) + float(match.p))
          else:
            match.p = "0.0"
          match.f = datetime.datetime.now().toordinal()
      if age:
        match.age = int(age)
      #match.a = calcRMR(match.gender, match.weight, match.height, match.age, match.b, match.c)
      match.a = 100
      db.session.commit()
      flash("SSuccessfully Updated Biometric Data!")
      return redirect(url_for("my_account"))
  return render_template("myaccount.html", 
                         uname=session.get("uname"), 
                         email=match.email, 
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
    # if not match.gender or not match.weight or not match.height or not match.age:
    #   flash("DPlease set your gender, weight, height, and age first!")
    #   return redirect(url_for("my_account"))
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
  # if not match.gender or not match.weight or not match.height or not match.age:
  #     flash("DPlease set your gender, weight, height, and age first!")
  #     return redirect(url_for("my_account"))
  activity = activity_mets[id]
  # match.a = calcRMR(match.gender, match.weight, match.height, match.age, match.b, match.c)
  cals = get_calories(activity[1], match.a , match.d)
  match.day_calories_burned += cals
  match.week_calories_burned += cals
  match.month_calories_burned += cals
  match.year_calories_burned += cals
  match.j += str(activity[3]) + "|" + str(mins) + "\n"
  if(match.r):
    match.h += int(float(activity[2]))
    match.i += 1
    match.r = str((float(datetime.datetime.now().toordinal()) - float(match.g)) / (MS_PER_DAY * 7.0 / 1000.0) + float(match.r))
  else:
    match.r = "0.0"
  match.g = datetime.datetime.now().toordinal()
  db.session.commit()
  flash(f"SSuccessfully completed {activity[1]} for {mins} minutes!")
  return redirect(url_for("index"))


if __name__ == "__main__":
  app.run(debug=True)