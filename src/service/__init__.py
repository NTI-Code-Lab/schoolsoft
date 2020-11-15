from os import getenv
from dotenv import load_dotenv
from ..api import SchoolSoft
from ..helper import classID
from ..database import *

# load the env file
load_dotenv()

username, password = getenv('username'), getenv('password')
api = SchoolSoft(username=username, password=password)

classList = [
    'HA18',
    'HA19',
    'IT20',
    'IT19',
    'IT18',
    'TE20',
    'TE19',
    'TE18'
]


def ScheduleTask():
    """
    Run schedule function and update the database for each class
    """

    # Store the result of the api call
    data = []
    # Loop for each class in classList
    for name in classList:
        # Get class name
        id = classID(name)
        print(id)
        # Request for the data from SchoolSoft
        # Api.schedule return type List
    #     response = api.schedule(id)
    #     # Create a loop of the week and set the index as day
    #     # The week starts from Monday until Friday
    #     # Example: indexOfMonday = 0
    #     for day in range(4):
    #         # Get the day schedule
    #         for block in response[day].schedule:
    #             # Make sure it's not a break
    #             if not block.is_break:
    #                 # Remove \r\n from the string
    #                 location = str(block.location).replace('\r\n', ' ')
    #                 # Append the data to the data list
    #                 data.append({'subject': block.subject,
    #                              'time': block.time, 'location': location})
    # # connect to the database
    # connect()
    # # create schedule and save it to the database
    # createSchedule(data)
    # # disconnect from the database
    # disconnect()
    # print that the task is done
    print("Corn task complete")
