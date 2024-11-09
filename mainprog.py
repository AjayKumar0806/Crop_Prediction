from flask import Flask, render_template, request, session, flash
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")  # Update with your actual file name
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://farmse-2cd34-default-rtdb.firebaseio.com'  # Your Firebase Database URL
})

@app.route('/')
def home():
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

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['Name']
            phonno = request.form['MobileNumber']
            email = request.form['email']
            unm = request.form['Username']
            passwd = request.form['password']
            # Reference path where the data will be stored in Firebase
            user_ref = db.reference(f'agriuser/{unm}')
            # Setting the data in Firebase Realtime Database
            user_ref.set({
                'name': nm,
                'phone': phonno,
                'email': email,
                'username': unm,
                'password': passwd
            })
            msg = "Record successfully added"
        except Exception as e:
            msg = f"Error in insert operation: {str(e)}"
        return render_template("result.html", msg=msg)

@app.route('/userlogin')
def user_login():
    return render_template("login.html")

@app.route('/logindetails', methods=['POST', 'GET'])
def logindetails():
    if request.method == 'POST':
        usrname = request.form['username']
        passwd = request.form['password']

        # Check user credentials in Firebase
        user_ref = db.reference(f'agriuser/{usrname}')
        user_data = user_ref.get()

        if user_data and user_data['password'] == passwd:
            session['logged_in'] = True
            return render_template('home.html')
        else:
            flash("Invalid user credentials")
            return render_template('login.html')

@app.route('/predictinfo')
def predictin():
    return render_template('info.html')

@app.route('/predict', methods=['POST', 'GET'])
def predcrop():
    if request.method == 'POST':
        comment = request.form['comment']
        comment1 = request.form['comment1']
        comment2 = request.form['comment2']
        data = comment
        data1 = comment1
        data2 = int(comment2)
        
        # Data processing logic...
        # This part remains unchanged from your original code.
        
        # Placeholder for your prediction logic and response
        response = "Suggested Crop 1"  # Replace with your actual prediction logic
        res12 = "Price for Crop 1"  # Replace with your actual price logic
        response2 = "Suggested Crop 2"  # Replace with your actual prediction logic
        res13 = "Price for Crop 2"  # Replace with your actual price logic

        return render_template('resultpred.html', prediction=response, price=res12, prediction1=response2, price1=res13)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
