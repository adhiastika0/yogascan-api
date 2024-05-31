from flask import Flask, request
from flask_restful import Resource, Api
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase app
cred = credentials.Certificate("./serviceAccount.json")
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Flask application
app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def post(self):
        try:
            # Add a document to the 'user' collection
            db.collection('user').add({'uid': 'random', 'username': 'Adhi', 'profile_picture': 'test'})
            return {"message": "Document added successfully"}, 201
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500

# Add resource to API
api.add_resource(HelloWorld, '/')

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
