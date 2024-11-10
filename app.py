# from flask import Flask,render_template
from flask import Flask, render_template, request, session, flash
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase-adminsdk.json")  # Update the path to your service account key
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://farmse-2cd34-default-rtdb.firebaseio.com/'  # Replace with your Firebase Database URL
})

app =   Flask(__name__)

@app.route('/') 
def index(): 
    return render_template('index.html') 

@app.route('/gohome')
def homepage():
    return render_template('index.html')

@app.route('/service')
def servicepage():
    return render_template('services.html')

@app.route('/coconut')
def coconutpage():
    return render_template('Coconut.html')

@app.route('/cocoa')
def cocoapage():
    return render_template('cocoa.html')

@app.route('/arecanut')
def arecanutpage():
    return render_template('arecanut.html')

@app.route('/paddy')
def paddypage():
    return render_template('paddy.html')

@app.route('/about')
def aboutpage():
    return render_template('about.html')

@app.route('/enternew')
def new_user():
    return render_template('signup.html')

@app.route('/addrec', methods=['POST'])
def addrec():
    if request.method == 'POST':
        try:
            user_data = {
                'name': request.form['Name'],
                'phone': request.form['MobileNumber'],
                'email': request.form['email'],
                'username': request.form['Username'],
                'password': request.form['password']
            }
            # Add user to Realtime Database
            ref = db.reference('agriuser')
            ref.push(user_data)  # Use push to generate a unique key
            msg = "Record successfully added"
        except Exception as e:
            msg = f"Error in insert operation: {e}"
        return render_template("result.html", msg=msg)

@app.route('/userlogin')
def user_login():
    return render_template("login.html")

@app.route('/logindetails', methods=['POST'])
def logindetails():
    if request.method == 'POST':
        usrname = request.form['username']
        passwd = request.form['password']

        # Query Realtime Database to validate user credentials
        ref = db.reference('agriuser')
        users = ref.get()

        # Check if any user has the provided credentials
        valid_user = any(user['username'] == usrname and user['password'] == passwd for user in users.values())

        if valid_user:
            session['logged_in'] = True
            return render_template('home.html')
        else:
            flash("Invalid user credentials")
            return render_template('login.html')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')

if __name__ == '__main__': 
    app.run(debug=True)