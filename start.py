from flask import Flask, render_template, redirect, url_for
from src.utils.Utils import Logger
from src.restAPI.resorces import courses


app = Flask(
    __name__,
    template_folder="src/restAPI/build/templates",
    static_folder="src/restAPI/build/static"
)

logger = Logger(__name__).get_logger()

api_version = "/api/v1"

app.register_blueprint(courses.courses, url_prefix=api_version)


@app.route(
    rule="/",
    endpoint="to_index"
)
def to_index():
    return redirect(url_for("index"))


@app.route(
    rule=api_version,
    endpoint="index"
)
def index():
    return render_template("index.html")


def run():
    logger.info("Rest server is started...")
    app.run()


if __name__ == "__main__":
    run()
