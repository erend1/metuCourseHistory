import mongoengine
import pandas as pd

from src.mainAPI.courses.db.Query import QueryPipeline
from src.mainAPI.courses.db.Connector import main_conn
from src.utils.Utils import Logger, get_doc_name
import src.mainAPI.courses.db.MongoDB as db


# Define logger object.
logger = Logger(__name__).get_course_logger()


class Course:
    def __init__(
            self,
            course_id: int = None
    ):
        self.id = course_id
        if not main_conn.online:
            main_conn.connect()

    # -------HELPER FUNCTIONS--------
    @staticmethod
    def _query_helper(query: QueryPipeline, operations: dict, steps: int):
        steps = range(steps)
        for index in steps:
            for func, temp_query in operations.items():
                if index in temp_query:
                    try:
                        getattr(query, func)(*temp_query[index])
                    except AttributeError as err:
                        logger.error(
                            f"Query object does not have given operation: {err}"
                        )
        return query

    # -------LOOKUP FUNCTIONS--------
    def schedule_look_up(
            self
    ) -> QueryPipeline:

        day_doc_name = get_doc_name(db.Day)
        time_doc_name = get_doc_name(db.Time)
        class_doc_name = get_doc_name(db.Class)
        join_tables = {
            0: [day_doc_name, "courseDay", "_id", "courseDay"],
            1: [time_doc_name, "courseTime", "_id", "courseTime"],
            2: [class_doc_name, "courseClass", "_id", "courseClass"],
        }
        unwind_tables = {
            0: ["courseDay"],
            1: ["courseTime"],
            2: ["courseClass"],
        }
        operations = {
            "join": join_tables,
            "parallelize": unwind_tables,
        }
        query = QueryPipeline(
            root_document=db.Schedule,
            allow_disk_usage=True
        )
        query = self._query_helper(
            query=query,
            operations=operations,
            steps=3
        )
        return query

    def record_look_up(
            self
    ) -> QueryPipeline:
        semester_doc_name = get_doc_name(db.Semester)
        course_doc_name = get_doc_name(db.Course)
        instructor_doc_name = get_doc_name(db.Instructor)
        schedule_doc_name = get_doc_name(db.Schedule)
        join_tables = {
            0: [semester_doc_name, "semester", "_id", "semester"],
            1: [course_doc_name, "course", "_id", "course"],
            2: [instructor_doc_name, "instructor", "_id", "instructor"],
            3: [schedule_doc_name, "schedule", "_id", "schedule"],
        }
        unwind_tables = {
            0: ["semester"],
            1: ["course"],
            2: ["instructor"],
        }
        match_conditions = {
            1: [{"course._id": self.id}]
        }
        operations = {
            "join": join_tables,
            "parallelize": unwind_tables,
            "match": match_conditions
        }
        query = QueryPipeline(
            root_document=db.Record,
            allow_disk_usage=True
        )
        query = self._query_helper(
            query=query,
            operations=operations,
            steps=4
        )
        return query

    # -------APPLICATION FUNCTIONS--------
    def get_course(
            self
    ) -> db.Course:
        course = db.Course.objects(
            id=self.id
        ).first()
        return course

    def get_course_name(
            self
    ) -> str:
        course = self.get_course()
        if hasattr(course, "name"):
            course = course.name
        return course

    def get_records(
            self
    ) -> QueryPipeline:
        query = self.record_look_up()
        new_fields = {
            "semesterId": "semester._id",
            "semesterName": "semester.name",
            "courseId": "course._id",
            "courseName": "course.name",
            "courseType": "course.type",
            "courseLevel": "course.level",
            "courseScheduler": "course.scheduler",
            "courseService": "course.service",
            "courseCredit": "course.credit",
            "courseCreditECTS": "course.creditECTS",
            "courseCreditLaboratory": "course.creditLaboratory",
            "courseCreditTheory": "course.creditTheory",
            "courseCreditApplication": "course.creditApplication",
            "courseSection": "section",
            "courseCapacity": "capacity",
            "courseCapacityExchange": "capacityExchange",
            "courseCapacityExchangeUsed": "capacityExchangeUsed",
            "courseStatus": "status",
            "instructorName": "instructor.name",
            "instructorTitle": "instructor.title"
        }

        for key, value in new_fields.items():
            query.add_field(
                key=key,
                value=value
            )
        query.keep(
            *new_fields.keys()
        ).remove(
            "_id"
        )
        return query

    def get_records_df(
            self
    ) -> pd.DataFrame:
        records = self.get_records().run()
        data_frame = pd.DataFrame(
            data=records
        )
        return data_frame

    def get_all_course_ids(
            self
    ) -> list:
        query = QueryPipeline(
            root_document=db.Course
        ).group(
            main_field="_id"
        ).add_field(
            key="label",
            value="_id"
        ).remove("_id")

        course_ids = list(
            query.run()
        )

        return course_ids


if __name__ == "__main__":
    api = Course(
        2360111
    )
    all_records = api.get_records_df()
    print(
        all_records
    )
    print(
        api.get_all_course_ids()
    )
