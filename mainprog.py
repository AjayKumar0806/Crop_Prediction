from flask import Flask, render_template, request, session, flash
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import math
import operator
import csv

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-adminsdk.json")  # Update the path to your service account key
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://farmse-2cd34-default-rtdb.firebaseio.com/'  # Replace with your Firebase Database URL
})

app = Flask(__name__)

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

@app.route('/predictinfo')
def predictin():
    return render_template('info.html')

def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):
        distance += (pow((float(instance1[x]) - float(instance2[x])), 2))
    return math.sqrt(distance)

def getNeighbors(trainingSet, testInstance, k):
    distances = []
    length = len(testInstance) - 1

    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors

def getResponse(neighbors):
    classVotes = {}
    for x in range(len(neighbors)):
        response = neighbors[x][-1]
        if response in classVotes:
            classVotes[response] += 1
        else:
            classVotes[response] = 1
    sortedVotes = sorted(classVotes.items(), key=operator.itemgetter(1), reverse=True)
    return sortedVotes[0][0]

def predict_crop(data, data1, data2):
    # Load the main data
    dff = pd.read_csv("data/maindata.csv")
    df1 = dff[dff['Location'].str.contains(data)]
    df2 = df1[df1['Soil'].str.contains(data1)]

    area = df2['Area']
    yeilds = df2['yeilds']
    price = df2['price']

    res2 = price / yeilds
    area_input = data2
    res3 = res2 * area_input
    res4 = (yeilds / area) * area_input

    # Save calculations to a CSV file
    df2.insert(11, "calculation", res3)
    df2.insert(12, "res4", res4)
    df2.to_csv('data/file.csv', index=False)

    # Prepare the training data
    data = pd.read_csv("data/file.csv", usecols=range(13))
    Type_new = pd.Series([])

    for i in range(len(data)):
        if data["Crops"][i] in ["Coconut", "Cocoa", "Coffee", "Cardamum", "Pepper", "Arecanut", "Ginger", "Tea"]:
            Type_new[i] = data["Crops"][i]
        else:
            Type_new[i] = data["Crops"][i]

    data.insert(13, "Crop val", Type_new)
    data.drop(["Year", "Location", "Soil", "Irrigation", "Crops", "yeilds", "calculation", "price"], axis=1, inplace=True)
    data.to_csv("data/train.csv", header=False, index=False)

    # Calculate averages for Rainfall, Temperature, and Humidity
    avg1 = data['Rainfall'].mean()
    avg2 = data['Temperature'].mean()
    avg3 = data['Humidity'].mean()

    testdata = {'Area': area_input, 'Rainfall': avg1, 'Temperature': avg2, 'Humidity': avg3}
    df7 = pd.DataFrame([testdata])
    df7.to_csv('data/test.csv', header=False, index=False)

    # Prepare training and test sets
    trainingSet = []
    testSet = []
    
    # Load training data
    with open('data/train.csv', 'r') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)
        for x in range(len(dataset) - 1):
            for y in range(5):
                dataset[x][y] = float(dataset[x][y])
            trainingSet.append(dataset[x])

    # Load test data
    with open('data/test.csv', 'r') as csvfile1:
        lines1 = csv.reader(csvfile1)
        dataset1 = list(lines1)
        for p in range(len(dataset1)):
            for q in range(4):
                dataset[p][q] = float(dataset[p][q])
            testSet.append(dataset1[p])

    k = 1
    neighbors = getNeighbors(trainingSet, testSet[0], k)
    response = getResponse(neighbors)

    # Suggesting second crop
    rem = response
    data1 = pd.read_csv("data/file.csv", usecols=range(13))
    val = data1[data1.Crops != rem]
    val.insert(13, "Cropval", Type_new)
    val.drop(["Year", "Location", "Soil", "Irrigation", "Crops", "yeilds", "calculation", "price"], axis=1, inplace=True)
    val.to_csv("data/train1.csv", header=False, index=False)

    trainingSet = []
    # Load modified training data
    with open('data/train1.csv', 'r') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)
        for x in range(len(dataset) - 1):
            for y in range(5):
                dataset[x][y] = float(dataset[x][y])
            trainingSet.append(dataset[x])

    neighbors = getNeighbors(trainingSet, testSet[0], k)
    response2 = getResponse(neighbors)

    return response, str(res2), response2, str(res12)

@app.route('/predict', methods=['POST', 'GET'])
def predcrop():
    if request.method == 'POST':
        comment = request.form['comment']
        comment1 = request.form['comment1']
        comment2 = request.form['comment2']

        # Validate the input for comment2
        if not comment2:  # Check if comment2 is empty
            flash("Please enter a valid number for the third input.")
            return render_template('info.html')  # Return to the input page

        try:
            data = comment
            data1 = comment1
            data2 = int(comment2)  # Convert to integer here

            response, res12, response2, res13 = predict_crop(data, data1, data2)

            return render_template('resultpred.html', prediction=response, price=res12, prediction1=response2, price1=res13)

        except ValueError:
            flash("Please enter a valid number for the third input.")
            return render_template('info.html')  # Return to the input page

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key
