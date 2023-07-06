from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
  cursor = mysql.connection.cursor()
  # cursor.execute('CREATE TABLE users (user_id INT PRIMARY KEY, username VARCHAR(50), password VARCHAR(50));')
  # cursor.execute('CREATE TABLE customers (customer_id INT PRIMARY KEY, user_id INT, FOREIGN KEY(user_id) REFERENCES users(user_id));')
  cursor.example('INSERT INTO users (user_id, username, password) VALUES (1, "admin", "admin");')
  mysql.connection.commit()
  cursor.close()
  return "Tables Created!"

if __name__ == '__main__':
  app.run(debug=True)