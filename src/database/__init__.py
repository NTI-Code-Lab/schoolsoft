import mongoengine
import datetime


class Schedule(mongoengine.Document):
    lesson = mongoengine.fields.DynamicField()
    creation_date = mongoengine.DateTimeField()
    modified_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.datetime.now()
        self.modified_date = datetime.datetime.now()
        return super(Schedule, self).save(*args, **kwargs)


def connect():
    mongoengine.connect(db='nti', host='localhost', port=27017)


def disconnect():
    mongoengine.disconnect()


def createSchedule(lesson=None):
    try:
        schedule = Schedule(lesson=lesson)
        schedule.save()
        return schedule.id
    except mongoengine.errors.NotUniqueError as e:
        print("NotUniqueError")
