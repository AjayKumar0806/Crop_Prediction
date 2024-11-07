import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK with your service account key
cred = credentials.Certificate("firebase-adminsdk.json") # Replace with your file path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://farmse-2cd34-default-rtdb.firebaseio.com'  # Replace with your Firebase Database URL
})

def add_agri_user(name, phono, email, username, password):
    # Reference path where the data will be stored in Firebase
    user_ref = db.reference(f'agriuser/{username}')
    
    # Setting the data in Firebase Realtime Database
    user_ref.set({
        'name': name,
        'phono': phono,
        'email': email,
        'username': username,
        'password': password
    })
    print("User added successfully!")

# Example usage
add_agri_user("John Doe", "1234567890", "johndoe@example.com", "john_doe", "securePassword123")
