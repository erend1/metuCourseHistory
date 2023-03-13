from flask import Blueprint, render_template, url_for, request, redirect
from src.mainAPI.courses.Courses import Course
from src.utils.Utils import courses_index_form


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
    data_frame = course.get_records_df()
    data_frame = data_frame.to_html(
        index=False,
        justify="center",
        col_space=120,
        show_dimensions=True
    ).replace(
        "class=\"dataframe\"",
        "class =\"table table-striped-responsive\""
    )

    return render_template(
        template_name_or_list="/courses/result.html",
        data_frame=data_frame,
        course_id=course_id,
        course_name=course_name
    )
