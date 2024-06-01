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

# Add resource to API
api.add_resource(HelloWorld, '/')
api.add_resource(Poses, '/getAllYogaPose')
api.add_resource(Pose, '/getYogaPose/<pose_id>')

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
