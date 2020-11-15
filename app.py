# Using flask to make an api
# import necessary libraries and functions
from sys import argv
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from time import gmtime, strftime

import calendar

from src import classID, SchoolSoft

# creating a Flask app
app = Flask(__name__)
api = Api(app)


class Schedule(Resource):
    def get(self, id):
        today = (int(strftime("%w", gmtime())) - 1)
        args = request.args
        data = []
        days = []
        print(args.get('day'))
        if args.get('day'):
            queryDay = list(calendar.day_name).index(
                str(args.get('day') if args.get('day') else 'monday').capitalize())
            print(queryDay)
            if not classID(str(id)):
                return {"message": "Invalid class id."}
            else:
                response = SchoolSoft(
                    'matin.akbari', 'HP@NTI5379902').schedule(classID(id))

                for block in response[queryDay].schedule:
                    if not block.is_break:
                        location = str(block.location).replace('\r\n', ' ')
                        data.append(
                            {'subject': block.subject, 'time': block.time, 'location': location})
                return jsonify(data)

        if args.get('today') == 'true':
            if today == 5 or today == 6:
                return {"message": "it's the weekend!"}
            else:
                if not classID(str(id)):
                    return {"message": "Invalid class id."}
                else:
                    response = SchoolSoft(
                        'matin.akbari', 'HP@NTI5379902').schedule(classID(id))

                    for block in response[today].schedule:
                        if not block.is_break:
                            location = str(block.location).replace('\r\n', ' ')
                            data.append(
                                {'subject': block.subject, 'time': block.time, 'location': location})

                    return jsonify(data)
        else:
            if not classID(str(id)):
                return {"message": "Invalid class id."}
            else:
                response = SchoolSoft(
                    'matin.akbari', 'HP@NTI5379902').schedule(classID(id))

                for day in range(5):
                    for block in response[day].schedule:
                        if not block.is_break:
                            location = str(block.location).replace('\r\n', ' ')
                            data.append({'subject': block.subject, 'time': block.time,
                                         'location': location, 'day': calendar.day_name[day]})

                return jsonify(data)


class Lunch(Resource):
    def get(self):
        args = request.args
        week = args.get('week')
        if args.get('week'):
            response = SchoolSoft(
                'matin.akbari', 'HP@NTI5379902').lunch(week)
            return jsonify(response)
        else:
            response = SchoolSoft('matin.akbari', 'HP@NTI5379902').lunch(-1)
            return jsonify(response)


class Root(Resource):
    def get(self):
        return jsonify({
            'developer': 'https://github.com/simple-max',
            'version': 'v1',
            'availablePath': ['lunch', 'schedule'],
            'queryParameters': [
                {'example': 'v1/schedule/class?day=monday',
                 'description': 'returns all the subject of that day', 'parameterType': 'string<day>'},
                {'example': 'v1/schedule/class?today=true',
                 'description': 'returns the current day subjectsy', 'parameterType': 'string<day>'}
            ]
        })


api.add_resource(Schedule, '/v1/schedule/<string:id>')
api.add_resource(Lunch, '/v1/lunch')
api.add_resource(Root, '/')

if __name__ == "__main__":
    app.run(debug=True)
