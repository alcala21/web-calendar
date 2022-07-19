from flask import Flask
from flask_restful import Api, Resource
import sys

app = Flask(__name__)

# write your code here
api = Api(app)


class EventsResource(Resource):
    def get(self):
        return {'data': 'There are no events for today!'}


api.add_resource(EventsResource, '/event/today')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
