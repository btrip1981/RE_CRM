from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_mysqldb import MySQL
import openai
import os
import logging
from tenacity import retry, stop_after_attempt, wait_fixed


max_attempts = 3
wait_seconds = 2

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = ""

logging.basicConfig(level=logging.DEBUG)

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

mysql = MySQL(app)

ADMIN_USERNAME = ''
ADMIN_PASSWORD = ''


# If the user is not logged in or doesn't have admin rights, this function redirect user to the login page.
def require_admin():
    if not session.get('logged_in') or not session.get('admin'):
     return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
    if password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['admin'] = True
        return redirect(url_for('dashboard'))
    else:
        error = 'Invalid password. Please try again.'
    return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin_console', methods=['GET', 'POST'])
def admin_console():
  require_admin()
  if request.method == 'POST':
    if request.form['password'] == ADMIN_PASSWORD:
     return redirect(url_for('admin_console'))
  return render_template('admin_console.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/customer/<int:cust_id>')
def customer_profile(cust_id):
    # Create a cursor
    cur = mysql.connection.cursor()
    # Retrieve the customer details from the 'customers' table
    query = "SELECT * FROM customers WHERE customer_id = %s"
    cur.execute(query, cust_id)
    customer = cur.fetchone()

    if customer:
        # Retrieve the associated properties for the customer
        query = "SELECT * FROM properties WHERE customer_id = %s"
        cur.execute(query, cust_id)
        properties = cur.fetchall()

        # Render the customer profile HTML template
        return render_template('customer_profile.html', customer=customer, properties=properties)
    else:
        # Handle the case when the customer does not exist
        return "Customer not found"


@app.route('/leads', methods=['GET'])
def get_leads():
    # Create a cursor
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customers")
    data = cur.fetchall()
    cur.close()
    return render_template('leads.html', data=data)

@app.route('/save_property', methods=['POST'])
def save_property():
    # Get the form data
    customer_id = request.form['customer_id']
    address_line1 = request.form['address_line1']
    address_line2 = request.form['address_line2']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zip']
    is_listing = request.form.get('is_listing', False)

    # Create a cursor
    cur = mysql.cursor()

    # Insert the property details into the 'properties' table
    insert_query = """
    INSERT INTO properties (customer_id, address_line1, address_line2, city, state, zip, is_listing)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(insert_query, (customer_id, address_line1, address_line2, city, state, zip_code, is_listing))


    mysql.commit()


    cur.close()

    return 'Property saved successfully'


@app.route('/newlead', methods=["GET", "POST"])
def newlead():
    # add new customer
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        phone = request.form.get("phone")

    # Create a cursor
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO customers
    (fname, lname, email, phone)
    VALUES (%s, %s, %s, %s);""",
                    (fname, lname, email, phone))

        mysql.connection.commit()
        cur.close()

        return "Data insertion successful", 200
    else:
        return render_template('newlead.html')


@app.route('/scheduleAppointment')
def scheduleAppointment():
    return render_template('scheduleAppointment.html')

@app.route('/customer_profile')
def customer_profile():
    return render_template('customer_profile.html')


@app.route('/adCampaign')
def adCampaign():
    return render_template('adCampaign.html')


@app.route('/generateDocument')
def generateDocument():
    return render_template('generateDocument.html')

@app.route('/pipeline')
def pipeline():
    return render_template('pipeline.html')

# openai API call
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    try:
        response = call_gpt4_api(data["messages"])
        return jsonify(response)
    # If there is an error, return the error
    except Exception as e:
        app.logger.error(f"Error in chat route: {e}")
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500

@retry(stop=stop_after_attempt(max_attempts), wait=wait_fixed(wait_seconds))
def call_gpt4_api(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == '__main__':
    app.run(debug=True)