from flask import Flask
from flask_restful import Api
from resources.create_account import CreateAccount
from resources.login import Login
from resources.poses import Poses, Pose
from resources.favorites import getFavorite
from resources.history import History

# Flask application
app = Flask(__name__)
api = Api(app)

#Create Account
api.add_resource(CreateAccount, '/signup')

#Create Account
api.add_resource(Login, '/login')

#Pose 
api.add_resource(Poses, '/poses')
api.add_resource(Pose, '/pose/<pose_id>')

#Favorite
api.add_resource(getFavorite, '/favorite/<uid>')

#History
api.add_resource(History, '/history/<uid>')

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
