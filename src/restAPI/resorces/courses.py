from flask import Blueprint, render_template, url_for, request, redirect
from src.mainAPI.courses.Courses import Course
from src.utils.Utils import courses_index_form, convert_df_to_html


courses = Blueprint("courses", __name__, url_prefix="/courses")


@courses.route(
    rule="/courses",
    methods=["GET", "POST"],
    endpoint="index"
)
def index():
    if request.method == "POST":
        course_id, = courses_index_form(form=request.form)
        return redirect(
            url_for(
                'courses.result',
                course_id=course_id
            )
        )
    else:
        course_ids = Course().get_all_course_ids()
        return render_template(
            template_name_or_list="/courses/index.html",
            course_ids=course_ids
        )


@courses.route(
    rule="/courses/<int:course_id>/",
    endpoint="result"
)
def result(course_id: int):
    course = Course(course_id=course_id)
    course_name = course.get_course_name()
    course_info = convert_df_to_html(
        data=course.get_course_df()
    )
    records = convert_df_to_html(
        data=course.get_records_df(),
        index=False
    )
    return render_template(
        template_name_or_list="/courses/result.html",
        records=records,
        course_info=course_info,
        course_id=course_id,
        course_name=course_name
    )
