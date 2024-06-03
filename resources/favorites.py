from flask_restful import Resource
from flask import request
from firebase_setup import db
from firebase_admin import auth

class getFavorite(Resource):
    def get(self):
        try:
            #get token from header and decode it to uid
            token = request.headers.get('Authorization').split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
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
        
    def post(self):
        try:
            token = request.headers.get('Authorization').split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
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

    def delete(self):
        try:
            token = request.headers.get('Authorization').split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
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
