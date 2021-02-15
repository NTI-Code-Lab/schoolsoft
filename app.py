# Using flask to make an api
# import necessary libraries and functions
from sys import argv
from flask import Flask, json, jsonify, request
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
            days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
            data = []
            for day in range(0, 5):
                try:
                    if len(response[day]) != 2:
                        data.append({"day": days[day], "food": {
                                    "one": response[day][0]}})
                    else:
                        data.append(
                            {"day": days[day], "food": {
                                "one": response[day][0], "two": response[day][1]}}
                        )
                except Exception as e:
                    print(e)
            return jsonify(data)


class Contactlist(Resource):
    def get(self):
        response = SchoolSoft('matin.akbari', 'HP@NTI5379902').contactlist()
        try:
            return jsonify(response)
        except Exception as e:
            print(e)
            return 'errors with the server', 500


class Root(Resource):
    def get(self):
        return jsonify({
            'developer': 'https://github.com/simple-max',
            'version': 'v2',
            'availablePath': ['lunch', 'schedule', 'contactlist'],
            'queryParameters': [
                {'example': 'v2/schedule/class?day=monday',
                 'description': 'returns all the subject of that day', 'parameterType': 'string<day>'},
                {'example': 'v2/schedule/class?today=true',
                 'description': 'returns the current day subjectsy', 'parameterType': 'string<day>'},
                {'example': 'v2/contactlist',
                 'description': 'returns the current contactlist on schoolsoft'},
                {'example': 'v2/lunch',
                 'description': 'returns the lunch menu of the week on schoolsoft'}
            ]
        })


api.add_resource(Schedule, '/v2/schedule/<string:id>')
api.add_resource(Lunch, '/v2/lunch')
api.add_resource(Contactlist, '/v2/contactlist')
api.add_resource(Root, '/')

if __name__ == "__main__":
    app.run(debug=True)
