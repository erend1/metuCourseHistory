from mongoengine import *


class Semester(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length=200)


class Program(Document):
    id = IntField(primary_key=True)
    shortName = StringField(max_length=50)
    longName = StringField(max_length=200)


class Course(Document):
    id = IntField(primary_key=True)
    name = StringField(max_length=200)
    type = StringField(max_length=200)
    level = StringField(max_length=200)
    scheduler = StringField(max_length=200)
    service = BooleanField()
    credit = IntField()
    creditECTS = FloatField()
    creditLaboratory = FloatField()
    creditTheory = FloatField()
    creditApplication = FloatField()


class Instructor(Document):
    name = StringField(max_length=200)
    title = StringField(max_length=200)


class Class(Document):
    building = StringField(max_length=200)
    room = StringField(max_length=200)


class Time(Document):
    start = StringField(max_length=10)
    end = StringField(max_length=10)


class Day(Document):
    day = StringField(primary_key=True)


class Schedule(Document):
    courseClass = ReferenceField(Class)
    courseTime = ReferenceField(Time)
    courseDay = ReferenceField(Day)


class Record(Document):
    semester = ReferenceField(Semester)
    course = ReferenceField(Course)
    section = IntField()
    capacity = IntField()
    capacityExchange = IntField()
    capacityExchangeUsed = IntField()
    status = StringField()
    schedule = ListField(ReferenceField(Schedule))
    instructor = ReferenceField(Instructor)

