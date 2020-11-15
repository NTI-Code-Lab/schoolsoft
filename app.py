# Using flask to make an api
# import necessary libraries and functions
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

                for index in range(4):
                    for block in response[index].schedule:
                        if not block.is_break:
                            location = str(block.location).replace('\r\n', ' ')
                            data.append(
                                {'subject': block.subject, 'time': block.time, 'location': location})

                return jsonify(data)


class Lunch(Resource):
    def get(self):
        response = SchoolSoft('matin.akbari', 'HP@NTI5379902').lunch()
        return jsonify(response)


api.add_resource(Schedule, '/v1/schedule/<string:id>')
api.add_resource(Lunch, '/v1/lunch')

if __name__ == "__main__":
    app.run(debug=True)