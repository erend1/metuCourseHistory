from mongoengine import Q
import time
from src.utils.Utils import Logger, semester_id, schedule_index
from src.mainAPI.courses.db.Connector import main_conn
from src.mainAPI.courses.db import MongoDB as db


saver_logger = Logger(__name__).get_saver_logger()


# -----MAIN FEED CLASS------
class Feed:
    def __init__(self, data: dict = None, document_class=None):
        # Define each of these above variables.
        self._define_connection()

        # Main data object.
        self.data = data or dict()

        # Main MongoDB Document Object.
        self.doc_cls = document_class

        # Define valid data flag.
        self.valid_data = self._check_data()

        # Candidate document object.
        self.candidate_obj = None

    def _run_definer(
            self,
            function: str,
            *args,
            defining_obj: str = None,
            evaluate_time: bool = False
    ):
        try:
            fun = getattr(self, function)
        except AttributeError:
            saver_logger.error(f"Given function did not defined: {function}")
        else:
            try:
                if evaluate_time:
                    obj = defining_obj or function
                    tick = time.time()
                    fun(*args)
                    tock = time.time()
                    saver_logger.info(
                        f"Total Time to Execute/Construct {obj}: {tock - tick}"
                    )
                else:
                    fun(*args)
            except TypeError:
                saver_logger.error(
                    "Given function could not be called, "
                    f"please check input *args of the function: {function}"
                )

    def _check_data(self, data: dict = None):
        data = data or self.data or dict()
        if isinstance(data, dict):
            if len(data) != 0:
                return True
        return False

    def _define_connection(self):
        main_conn.connect()
        return self

    def _rename(self, mapper: dict, new_dict: bool = True):
        if not new_dict:
            data = self.data
        else:
            data = dict()

        for key, value in mapper.items():
            if key in self.data:
                data[value] = self.data.pop(key)

        self.data = data
        return self

    def get(self):
        if not self.valid_data:
            return None
        elif self.candidate_obj is not None:
            return self.candidate_obj
        else:
            result = self.doc_cls(
                **self.data
            ).save()
            return result


# -----SUBCLASSES------
class Semester(Feed):
    def __init__(self, semester_data: dict):
        super().__init__(
            semester_data, db.Semester
        )
        try:
            self.id = semester_id(
                semester_name=self.data["Semester"]
            )
        except KeyError:
            saver_logger.error(
                f"Semester key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            semester_data["id"] = self.id
            self._rename(
                mapper={
                    "id": "id",
                    "Semester": "name"
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            semester_doc = self.doc_cls.objects(
                Q(id=self.id)
            ).first()
            return semester_doc


class Program(Feed):
    def __init__(self, program_data: dict):
        super().__init__(
            program_data, db.Program
        )
        try:
            self.id = self.data["Program Code"]
        except KeyError:
            saver_logger.error(
                f"Program Code key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self._rename(
                mapper={
                    "Program Code": "id",
                    "Program Short Name": "shortName",
                    "Program Long Name": "longName"
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            program_doc = self.doc_cls.objects(
                Q(id=self.id)
            ).first()
            return program_doc


class Course(Feed):
    def __init__(self, course_data: dict):
        super().__init__(
            course_data, db.Course
        )
        try:
            self.id = self.data["Course Code"]
        except KeyError:
            saver_logger.error(
                f"Course Code key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self._rename(
                mapper={
                    "Course Code": "id",
                    "Course Name": "name",
                    "Course Type": "type",
                    "Course Level": "level",
                    "Service Course": "service",
                    "Course Scheduler": "scheduler",
                    "Credit": "credit",
                    "ECTS Credit": "creditECTS",
                    "Laboratory Credit": "creditLaboratory",
                    "Theory Credit": "creditTheory",
                    "Application Credit": "creditApplication",
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            program_doc = self.doc_cls.objects(
                Q(id=self.id)
            ).first()
            return program_doc


class Instructor(Feed):
    def __init__(self, instructor_data: dict):
        super().__init__(
            instructor_data, db.Instructor
        )
        try:
            self.name = self.data["Instructor Name"]
            self.title = self.data["Instructor Title"]
        except KeyError:
            saver_logger.error(
                f"Instructor Name or Instructor Title key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self._rename(
                mapper={
                    "Instructor Name": "name",
                    "Instructor Title": "title"
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            program_doc = self.doc_cls.objects(
                Q(name=self.name) & Q(title=self.title)
            ).first()
            return program_doc


class Class(Feed):
    def __init__(self, class_data: dict):
        super().__init__(
            class_data, db.Class
        )
        try:
            self.building = self.data["Classroom Building"]
            self.room = self.data["Classroom"]
        except KeyError:
            saver_logger.error(
                f"Classroom Building or Classroom key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self._rename(
                mapper={
                    "Classroom Building": "building",
                    "Classroom": "room"
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            program_doc = self.doc_cls.objects(
                Q(building=self.building) & Q(room=self.room)
            ).first()
            return program_doc


class Time(Feed):
    def __init__(self, time_data: dict):
        super().__init__(
            time_data, db.Time
        )
        try:
            self.start = self.data["Start Hour"]
            self.end = self.data["End Hour"]
        except KeyError:
            saver_logger.error(
                f"Start or End Hour key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self._rename(
                mapper={
                    "Start Hour": "start",
                    "End Hour": "end"
                }
            )
            self.candidate_obj = self._find_doc()

    def _find_doc(self):
        if self.valid_data:
            program_doc = self.doc_cls.objects(
                Q(start=self.start) &
                Q(end=self.end)
            ).first()
            return program_doc


class Day(Feed):
    def __init__(self, day_data: dict):
        super().__init__(
            day_data, db.Day
        )
        try:
            self.id = self.data["Day"]
        except KeyError:
            saver_logger.error(
                f"Day could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self.candidate_obj = self._find_doc()

        if self.candidate_obj is None:
            self._rename(
                mapper={
                    "Day": "day"
                }
            )

    def _find_doc(self):
        if self.valid_data:
            day_doc = self.doc_cls.objects(
                Q(day=self.id)
            ).first()
            return day_doc


class Schedule(Feed):
    def __init__(self, schedule_data: dict):
        super().__init__(
            schedule_data, db.Schedule
        )
        self.course_class = None
        self._run_definer(
            function="_define_class",
            defining_obj="Class"
        )
        self.course_day = None
        self._run_definer(
            function="_define_day",
            defining_obj="Day"
        )
        self.course_time = None
        self._run_definer(
            function="_define_time",
            defining_obj="Time"
        )
        self.candidate_obj = self._find_doc()

        if self.candidate_obj is None:
            self._rename(
                mapper={
                    "courseDay": "courseDay",
                    "courseTime": "courseTime",
                    "courseClass": "courseClass"
                }
            )

    def _find_doc(self):
        if self.valid_data:
            schedule_doc = self.doc_cls.objects(
                Q(courseDay=self.course_day) &
                Q(courseTime=self.course_time) &
                Q(courseClass=self.course_class)
            ).first()
            return schedule_doc

    def _define_class(self):
        if self.valid_data:
            class_obj = Class(
                class_data=self.data
            ).get()
            self.data["courseClass"] = self.course_class = class_obj

        return self

    def _define_time(self):
        if self.valid_data:
            time_obj = Time(
                time_data=self.data
            ).get()
            self.data["courseTime"] = self.course_time = time_obj
        return self

    def _define_day(self):
        if self.valid_data:
            day_obj = Day(
                day_data=self.data
            ).get()
            self.data["courseDay"] = self.course_day = day_obj
        return self


# -----RECORD CLASS------
class Record(Feed):
    def __init__(self, data: dict):
        super().__init__(
            data, db.Record
        )
        self._run_definer(
            function="_define_semester",
            defining_obj="Semester"
        )
        self._run_definer(
            function="_define_course",
            defining_obj="Course"
        )
        try:
            self.semester = self.data["semester"]
            self.course = self.data["course"]
            self.section = self.data["Course Section"]
        except KeyError:
            saver_logger.error(
                f"Semester or Course Code or Section key could not be found: {self.data}"
            )
            self.valid_data = False
        else:
            self.candidate_obj = self._find_doc()

        if self.candidate_obj is None:
            self._run_definer(
                function="_define_schedule",
                defining_obj="Schedule"
            )
            self._run_definer(
                function="_define_instructor",
                defining_obj="Instructor"
            )
            self._rename(
                mapper={
                    "semester": "semester",
                    "course": "course",
                    "Course Section": "section",
                    "Capacity": "capacity",
                    "Exchange Capacity": "capacityExchange",
                    "Exchange Used Capacity": "capacityExchangeUsed",
                    "Course Status": "status",
                    "schedule": "schedule",
                    "instructor": "instructor",
                }
            )

    def _find_doc(self):
        if self.valid_data:
            record_doc = self.doc_cls.objects(
                Q(semester=self.semester) &
                Q(course=self.course) &
                Q(section=self.section)
            ).first()
            return record_doc

    def _define_semester(self):
        if self.valid_data:
            semester_obj = Semester(
                semester_data=self.data
            ).get()
            self.data["semester"] = semester_obj
        return self

    def _define_course(self):
        if self.valid_data:
            course_obj = Course(
                course_data=self.data
            ).get()
            self.data["course"] = course_obj
        return self

    def _define_schedule(self):
        if self.valid_data:
            max_schedule = 6
            schedule = list()
            for _ in range(max_schedule):
                schedule.append(dict())
            features = [
                "Day",
                "Start Hour",
                "End Hour",
                "Classroom Building",
                "Classroom"
            ]
            for key, value in self.data.items():
                if value is None:
                    continue
                for column in features:
                    if column in key:
                        index = schedule_index(key, column)
                        schedule[index][column] = value
                        break
            schedule_objs = list()
            for data in schedule:
                if len(data) != 0:
                    schedule_objs.append(
                        Schedule(
                            schedule_data=data
                        ).get()
                    )
            self.data["schedule"] = schedule_objs
        return self

    def _define_instructor(self):
        if self.valid_data:
            instructor_obj = Instructor(
                instructor_data=self.data
            ).get()
            self.data["instructor"] = instructor_obj
        return self
