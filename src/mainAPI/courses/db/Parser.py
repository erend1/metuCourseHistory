import json
import pandas as pd
import time
from src.mainAPI.courses.db.Helper import Record
from src.utils.Utils import Logger, get_src_path


default_path = get_src_path("\\data\\")
default_file = "SearchResults.xlsx"
parser_logger = Logger(__name__).get_parser_logger()


# -----PARSER CLASS------
class Parser:
    def __init__(self):
        self.data = None
        self.data_df = None
        self.file = None
        self.path = None
        self.load_flag = False

    def _load_json(self):
        if not self.load_flag:
            return self
        data = self.data_df.to_json(
            index=False,
            orient="table"
        )
        self.data = json.loads(data)["data"]
        return self

    def load(
            self,
            file: str = None,
            path: str = None
    ):
        self.file = file or default_file
        self.path = path or default_path
        try:
            self.data_df = pd.read_excel(
                io=self.path + self.file
            )
            self.load_flag = True

        except Exception as err:
            parser_logger.error(
                f"While reading data following error occurred: {err}"
            )
            self.load_flag = False
            return self

        else:
            return self._load_json()

    def parse(self):
        if self.load_flag:
            if isinstance(self.data, list):
                tick = time.time()
                for data in self.data:
                    Record(
                        data=data
                    ).get()
                tock = time.time()
                parser_logger.info(
                    f"Following file successfully parsed: {self.file}. "
                    f"Total time it takes: {tock - tick}"
                )
        return self


if __name__ == "__main__":
    def saver(index: int = None):
        file_name = "SearchResults "
        if index is None:
            file_index = ""
        else:
            file_index = f"({index})"
        file_tag = ".xlsx"
        file = file_name + file_index + file_tag
        Parser().load(
            file=file
        ).parse()
    for i in range(6, 29):
        print("START: ", i)
        saver(i)
        print("DONE: ", i)
