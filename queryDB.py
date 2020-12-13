from flask_sqlalchemy import SQLAlchemy

from main import db, User

while True:
  try:
    print([value for value in db.engine.execute(input("SQL Query: "))])
  except Exception as e:
    print(e)