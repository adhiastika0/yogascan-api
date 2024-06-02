from flask_restful import Resource
from firebase_setup import db

class HelloWorld(Resource):
    def post(self):
        try:
            # Add a document to the 'user' collection
            db.collection('user').add({'uid': 'random', 'username': 'Adhi', 'profile_picture': 'test'})
            return {"message": "Document added successfully"}, 201
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500
