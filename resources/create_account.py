from flask_restful import Resource
from flask import request
from firebase_setup import db
from firebase_admin import credentials, firestore, auth


class CreateAccount(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        username = data.get('username')


        if not email or not password or not username:
            return {"error": "Email, password, and username are required"}, 400

        try:
            # Buat pengguna baru
            user = auth.create_user(
                email=email,
                password=password
            )

            db.collection('user').add({'uid': user.uid, 'username': username, 'profile_picture': 'test'})

            return {
                "message": "Successfully created new user",
                "uid": user.uid
            }, 201
        except Exception as e:
            return {"error": str(e)}, 400

