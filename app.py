from flask import Flask, request
from flask_restful import Resource, Api
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz

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
        
class getFavorite(Resource):
    def get(self, uid):
        try:
            # Retrieve favorite poses for the user            
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = [doc.to_dict() for doc in favorite_ref]

            # Extract pose IDs
            if favorite_list:
                pose_ids = favorite_list[0]['pose']

                # Retrieve pose details
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
            # Retrieve favorite poses for the user
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = list(favorite_ref)
            
            if favorite_list:
                # Add the new pose_id to the existing favorite list
                doc_id = favorite_list[0].id 
                pose_list = favorite_list[0].to_dict()['pose']
                if pose_id not in pose_list:
                    pose_list.append(pose_id)
                    db.collection('favorite').document(doc_id).update({'pose': pose_list})
                    return {"message": "Pose added to favorites"}, 200
                else:
                    return {"message": "Pose already in favorites"}, 400
            else:
                # Create a new favorite document for the user
                db.collection('favorite').add({'uid': uid, 'pose': [pose_id]})
                return {"message": "Pose added to favorites"}, 201
        except Exception as e:
            return {"message": "An error occurred: " + str(e)}, 500

    def delete(self, uid):
        try:
            pose_id = request.json['pose_id']
            # Retrieve favorite poses for the user
            favorite_ref = db.collection('favorite').where('uid', '==', uid).stream()
            favorite_list = list(favorite_ref)
            
            if favorite_list:
                # Remove the pose_id from the existing favorite list
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
        
class History(Resource):
    def get(self, uid):
        try:
            # Retrieve documents from the 'history' collection where 'uid' matches the provided user ID
            history_ref = db.collection('history').where('uid', '==', uid).stream()
            history_list = [doc.to_dict() for doc in history_ref]

            # Check if the history list is empty and return a 404 error if no history is found
            if not history_list:
                return {"message": "No history found for user"}, 404

            result_list = []

            # Loop through each history entry
            for history in history_list[0]['history']:
                pose_id = history['pose_id']
                # Retrieve the pose details from the 'pose' collection where 'pose_id' matches
                pose_query = db.collection('pose').where('pose_id', '==', pose_id).stream()
                pose_list = [pose.to_dict() for pose in pose_query]

                # If the pose exists, prepare the history entry
                if pose_list:
                    pose_data = pose_list[0]
                    history_entry = {
                        "Date": history['date'].isoformat(),  # Convert date to ISO format for JSON serialization
                        "result": history['result'],
                        "pose": {
                            "pose_id": pose_data['pose_id'],
                            "pose_name": pose_data['pose_name'],
                            "pose_image": pose_data['pose_image'],
                            "pose_description": pose_data['pose_description']
                        }
                    }
                    result_list.append(history_entry)

            # Return the list of history entries
            return {"history": result_list}, 200

        except Exception as e:
            # Return an error message if any exception occurs
            return {"message": "An error occurred: " + str(e)}, 500

    def post(self, uid):
        try:
            # Parse the date string from the request body and convert it to a datetime object
            date_str = request.json['date']
            date = datetime.fromisoformat(date_str.rstrip('Z')).replace(tzinfo=pytz.UTC)
            pose_id = request.json['pose_id']
            result = request.json['result']

            # Retrieve documents from the 'history' collection where 'uid' matches the provided user ID
            history_ref = db.collection('history').where('uid', '==', uid).stream()
            history_list = list(history_ref)

            # Prepare a new history entry
            new_entry = {
                "date": date,
                "pose_id": pose_id,
                "result": result
            }

            if history_list:
                # If history exists for the user, append the new entry to the existing history
                doc_id = history_list[0].id
                existing_history = history_list[0].to_dict()['history']
                existing_history.append(new_entry)
                db.collection('history').document(doc_id).update({'history': existing_history})
            else:
                 # If no history exists, create a new document with the new entry
                db.collection('history').add({'uid': uid, 'history': [new_entry]})

            # Return a success message
            return {"message": "History entry added successfully"}, 201

        except Exception as e:
            # Return an error message if any exception occurs
            return {"message": "An error occurred: " + str(e)}, 500


# Add resource to API
api.add_resource(HelloWorld, '/')

#Pose 
api.add_resource(Poses, '/getAllYogaPose')
api.add_resource(Pose, '/getYogaPose/<pose_id>')

#Favorite
api.add_resource(getFavorite, '/getFavoritePoses/<uid>')

#history
api.add_resource(History, '/getPosesHistory/<uid>')


# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
