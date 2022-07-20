from flask import Flask, jsonify, abort
from flask_restful import Api, Resource, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import sys
import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'

api = Api(app)


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


class EventSchema(Schema):
    id = fields.Integer()
    event = fields.String()
    date = fields.Date("%Y-%m-%d")


db.create_all()
event_schema = EventSchema(many=True)


class EventResource(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('date',
            type=inputs.date,
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True)

        self.parser.add_argument('event',
            type=str,
            help="The event name is required!",
            required=True)

        self.range_parser = reqparse.RequestParser()
        self.range_parser.add_argument('start_time',
            type=inputs.date,
            help='The correct format is YYYY-MM-DD!',
            required=False)
        self.range_parser.add_argument('end_time',
            type=inputs.date,
            required=False)

    def get(self):
        args = self.range_parser.parse_args()
        if args['start_time'] and args['end_time']:
            st = args['start_time']
            et = args['end_time']
            events = Event.query.filter(Event.date.between(st, et)).all()
            return event_schema.dump(events)
        return event_schema.dump(Event.query.all())

    def post(self):
        args = self.parser.parse_args()
        event = Event(event=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()
        response = {'message': 'The event has been added!',
                    'event': args['event'],
                    'date': str(args['date'].strftime('%Y-%m-%d'))}
        return response


class TodayResource(Resource):
    def get(self):
        return event_schema.dump(Event.query.filter(Event.date == datetime.date.today()).all())


class EventByID(Resource):

    def get(self, event_id):
        event = event_schema.dump(Event.query.filter_by(id=event_id).all())
        if len(event) > 0:
            return event[0]
        return abort(404, "The event doesn't exist!")

    def delete(self, event_id):
        if Event.query.filter_by(id=event_id).delete():
            db.session.commit()
            return {'message': 'The event has been deleted!'}
        return abort(404, "The event doesn't exist!")


api.add_resource(EventResource, '/event')
api.add_resource(TodayResource, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
