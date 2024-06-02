from flask import Flask
from flask_restful import Api
from resources.hello_world import HelloWorld
from resources.poses import Poses, Pose
from resources.favorites import getFavorite
from resources.history import History

# Flask application
app = Flask(__name__)
api = Api(app)

# Add resource to API
api.add_resource(HelloWorld, '/')
api.add_resource(Poses, '/getAllYogaPose')
api.add_resource(Pose, '/getYogaPose/<pose_id>')
api.add_resource(getFavorite, '/getFavoritePoses/<uid>')
api.add_resource(History, '/getPosesHistory/<uid>')

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
