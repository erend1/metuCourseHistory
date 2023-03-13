import logging
import os
import sys

import pandas as pd


class Logger:
    """
    Logger class provides us to modify logging object
    with more simple syntax and more simple definitions,
    especially for the definitions of paths and log files.

    """
    def __init__(
            self,
            name: str = None,
            file_name: str = None,
            path: str = None,
            extra: dict = None
    ):
        self.name = name or __name__
        self.file_name = file_name or "main.log"
        self.path = path or get_src_path("\\src\\log\\")

        # Main Attributes
        self.logger = None
        self.formatter = None
        self.file_handler = None

        # Formats.
        self.extra = extra or dict()
        self.formats = list()

        # Level Attribute
        self._level = logging.WARNING

        # Define handlers and main attributes
        self._define_handlers()

    def _define_format(self) -> str:
        self.formats = [
            "levelname", "asctime", "name"
        ] + list(self.extra.keys()) + [
            "message"
        ]
        fmt = ""
        for format_str in self.formats:
            fmt += f"%({format_str})s: "
        fmt = fmt.rstrip().rstrip(":")
        return fmt

    def _define_handlers(self):
        # Define main logging object.
        self.logger = logging.getLogger(name=self.name)

        # Define formatter.
        fmt = self._define_format()
        self.formatter = logging.Formatter(fmt)

        # Define file handler.
        self.file_handler = logging.FileHandler(self.path + self.file_name)
        self.file_handler.setFormatter(self.formatter)

        # Configure main logging object with above definitions.
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(level=self._level)
        self.logger = logging.LoggerAdapter(self.logger, self.extra)
        return self

    def update_logger_attr(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self._define_handlers()

    def get_logger(self) -> logging.Logger:
        self.update_logger_attr(file_name="main.log")
        return self.logger

    def get_connector_logger(self):
        self._level = logging.INFO
        self.update_logger_attr(file_name="connect.log")
        return self.get_logger()

    def get_parser_logger(self):
        self._level = logging.INFO
        self.update_logger_attr(file_name="parser.log")
        return self.get_logger()

    def get_query_logger(self):
        self._level = logging.INFO
        self.update_logger_attr(file_name="query.log")
        return self.get_logger()

    def get_course_logger(self):
        self._level = logging.INFO
        self.update_logger_attr(file_name="course.log")
        return self.get_logger()

    def get_courses_logger(self):
        self._level = logging.INFO
        self.update_logger_attr(file_name="courses.log")
        return self.get_logger()


def get_src_path(
        append_src: str = None,
        include_src: bool = False,
        include_sys_path: bool = True,
) -> str:
    """
    The function returns the path of src file in the directory
    without depending on current working directory. It will be
    not applicable if the current working directory is out of the
    project file, as the main algorithm of the function is appending
    parent directory up to obtaining src directory it-self.

    Example usage can be, get_src_path(append_src='/src/input/')

    :param str append_src: Append new directory from src file.
    :param include_src: Include '/src/' in the obtained path string.
    :param bool include_sys_path: Append sys path list with obtained src path.
    :return: Resulting path string.
    """
    current_path = os.getcwd()
    max_iter = len(str(current_path).split("\\"))

    path = None
    iteration = 0
    while path is None and iteration < max_iter:
        candidate_path, candidate_directory = os.path.split(current_path)
        current_path = os.path.abspath(candidate_path)
        if candidate_directory == "src":
            path = current_path
            if include_sys_path:
                sys.path.append(path)
            break
        iteration += 1

    if path is None:
        path = ""

    if include_src:
        path = os.path.join(path, "src")
    if append_src:
        path += append_src
    if not os.path.isdir(path):
        os.makedirs(name=path)

    return path


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def convert_input_into_list(*params):
    converted_params = list()
    for param in params:
        if param is not None:
            if not isinstance(param, list):
                if isinstance(param, dict):
                    param = list(param.keys())
                elif isinstance(param, str) or isinstance(param, int):
                    param = [param]
                else:
                    try:
                        param = list(param)
                    except Exception as err:
                        print(f"CAUTION! Some items could not converted into 'list' type: {param}")
                        print(err)
                        param = list()
        converted_params.append(param)

    return tuple(converted_params)


def convert_input_into_int_list(*params_list):
    converted_params_lists = list()
    for param in params_list:
        if param is not None:
            if isinstance(param, list):
                temp_params_list = list()
                for item in param:
                    try:
                        item = int(item)
                    except Exception as err:
                        print(f"CAUTION! Some items could not converted into 'int' type: {item}")
                        print(err)
                    temp_params_list.append(item)
            else:
                temp_params_list = param
            converted_params_lists.append(temp_params_list)
        else:
            converted_params_lists.append(None)
    return tuple(converted_params_lists)


def convert_input_into_str_list(*params, remove_char=""):
    converted_params = list()
    for param in params:
        temp_param = None
        if param is not None:
            if hasattr(param, "__getitem__"):
                temp_param = list()
                for item in param:
                    try:
                        temp_param.append(str(item).replace(remove_char, ""))
                    except Exception as err:
                        print(f"CAUTION! Some items could not converted into str type: {item}")
                        print(err)
                        temp_param.append(item)
        converted_params.append(temp_param)
    return tuple(converted_params)


def round_values_in_list(float_list: list, rounding_number: int = None):
    norm = len(float_list)
    if rounding_number is None:
        rounding_number = 6
    try:
        rounding_number = int(rounding_number)
    except ValueError:
        print(f"Object could not converted into integer: {rounding_number}")
        return float_list

    for index in range(norm):
        temp_obj = float_list[index]
        try:
            temp_obj = float(temp_obj)
        except ValueError:
            print(f"Object could not converted into float: {temp_obj}")
            continue
        temp_obj = round(temp_obj, rounding_number)
        float_list[index] = temp_obj
    return float_list


def semester_id(semester_name: str, separation_char: str = "-"):
    codes = {
        "Fall": "1",
        "Spring": "2",
        "Summer School": "3"
    }
    if separation_char in semester_name:
        main_id = semester_name.split(
            separation_char
        )[0].strip()
        for key, value in codes.items():
            if key in semester_name:
                main_id += value
                break
        main_id = int(main_id)
        return main_id
    else:
        return None


def schedule_index(name: str, feature: str):
    if feature in name:
        index = int(
            name.replace(feature, "").strip()
        )
        return index
    else:
        return None


def courses_index_form(form: dict):
    params_dict = {
        "course_id": 0,
    }
    for key in params_dict:
        if key in form:
            temp_value = form[key]
            try:
                temp_value = int(temp_value)
            except ValueError:
                continue
            else:
                params_dict[key] = temp_value

    return tuple(params_dict.values())


def get_doc_name(doc: object) -> str:
    """
    The function takes 'Document' class as input, and returns the document name of the object
    that is stored in the MongoDB. The function could be useful for querying pipelines especially
    for the join operation, because for join operations it is required to use directly the
    document name of object in MongoDB.

    :param doc: Any class that is a subclass of mongoengine.document.Document class will be valid.
    :return: Document name stored in MongoDB
    :rtype: str
    """
    if hasattr(doc, "_meta"):
        if "collection" in doc._meta:
            return doc._meta["collection"]
        else:
            print("Document name could not be found !")
    else:
        print("The class of the input 'doc' object must be MongoEngine Document class or any superclass of it.")
    return str()


def convert_df_to_html(
        data: pd.DataFrame,
        index: bool = True
) -> str:
    html_string = data.to_html(
        index=index,
        justify="center",
        col_space=120,
        show_dimensions=True
    ).replace(
        "class=\"dataframe\"",
        "class =\"table table-striped\""
    )
    return html_string


