from flask_restful import Resource
from flask import request
from firebase_setup import db
from firebase_admin import auth
from datetime import datetime
import pytz

class History(Resource):
    def get(self):
        try:
            #get token from header and decode it to uid
            token = request.headers.get('Authorization').split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
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

    def post(self):
        try:
            token = request.headers.get('Authorization').split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
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
