import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase app
cred = credentials.Certificate("./serviceAccount.json")
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
