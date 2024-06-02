from flask import Flask, request
from flask_restful import Resource, Api
import firebase_admin
from firebase_admin import credentials, firestore, auth

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

class Poses(Resource):
    def get(self):
        try:
            poses_ref = db.collection('pose')
            poses = poses_ref.stream()
            pose_list = []
            for pose in poses:
                pose_dict = pose.to_dict()
                pose_dict['id'] = pose.id
                pose_list.append(pose_dict)
            return {"poses": pose_list}, 200
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500

class Pose(Resource):
    def get(self, pose_id):
        try:
            pose_query = db.collection('pose').where('pose_id', '==', pose_id).stream()
            pose_list = [pose.to_dict() for pose in pose_query]
            
            if len(pose_list) > 0:
                pose_data = pose_list[0]
                return {"pose": pose_data}, 200
            else:
                return {"message": "Pose not found"}, 404
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500
        
class getFavorite(Resource):
    def get(self, uid):
        try:
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = [doc.to_dict() for doc in favorite_ref]

            if favorite_list:
                pose_ids = favorite_list[0]['pose']

                pose_details = []
                for pose_id in pose_ids:
                    pose_query = db.collection('pose').where('pose_id', '==', pose_id).stream()
                    for pose in pose_query:
                        pose_details.append(pose.to_dict())

                return {"favorites": pose_details}, 200
            else:
                return {"message": "No favorite poses found"}, 404
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500
        
    def post(self, uid):
        try:
            pose_id = request.json['pose_id']
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = list(favorite_ref)
            
            if favorite_list:
                doc_id = favorite_list[0].id 
                pose_list = favorite_list[0].to_dict()['pose']
                if pose_id not in pose_list:
                    pose_list.append(pose_id)
                    db.collection('favorite').document(doc_id).update({'pose': pose_list})
                    return {"message": "Pose added to favorites"}, 200
                else:
                    return {"message": "Pose already in favorites"}, 400
            else:
                db.collection('favorite').add({'uid': uid, 'pose': [pose_id]})
                return {"message": "Pose added to favorites"}, 201
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500

    def delete(self, uid):
        try:
            pose_id = request.json['pose_id']
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = list(favorite_ref)
            
            if favorite_list:
                doc_id = favorite_list[0].id  
                pose_list = favorite_list[0].to_dict()['pose']
                if pose_id in pose_list:
                    pose_list.remove(pose_id)
                    db.collection('favorite').document(doc_id).update({'pose': pose_list})
                    return {"message": "Pose removed from favorites"}, 200
                else:
                    return {"message": "Pose not found in favorites"}, 404
            else:
                return {"message": "No favorite poses found for user"}, 404
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500


# Add resource to API
api.add_resource(HelloWorld, '/')

#Create Account
api.add_resource(CreateAccount, '/create-account')


#Pose 
api.add_resource(Poses, '/getAllYogaPose')
api.add_resource(Pose, '/getYogaPose/<pose_id>')

#Favorite
api.add_resource(getFavorite, '/getFavoritePoses/<uid>')


# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
