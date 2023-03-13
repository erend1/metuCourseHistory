import time
from src.utils.Utils import Logger, get_doc_name


# Define logger object.
logger = Logger(__name__).get_query_logger()


class QueryPipeline:
    def __init__(
            self,
            root_document,
            allow_disk_usage=False,
            log: bool = True
    ):
        self.document = root_document
        self.doc_name = get_doc_name(self.document)
        self.disk_usage = allow_disk_usage
        self.log_flag = log
        self.pipeline = []

    def match(self, conditions):
        self.pipeline.append({
            "$match": conditions
        })
        return self

    def keep(self, *params):
        temp_dict = {}
        for item in params:
            temp_dict[item] = True
        self.pipeline.append({
            "$project": temp_dict
        })
        return self

    def keep_with_condition(self, local_field, input_field, conditions):
        self.pipeline.append({
            "$project": {local_field: {"$filter": {"input": "$" + input_field, "as": input_field, "cond": conditions}}}
        })
        return self

    def set_union(self, new_field, *params):
        unions = list(params)
        for index in range(len(unions)):
            unions[index] = "$" + str(unions[index])
        self.pipeline.append({
            "$addFields": {new_field: {"$setUnion": unions}}
        })
        return self

    def concat_arrays(self, new_field, *params):
        concat_arrays = list(params)
        for index in range(len(concat_arrays)):
            concat_arrays[index] = "$" + str(concat_arrays[index])
        self.pipeline.append({
            "$addFields": {new_field: {"$concatArrays": concat_arrays}}
        })
        return self

    def merge_fields(self, new_field, *params):
        merged_fields = list(params)
        for index in range(len(merged_fields)):
            merged_fields[index] = "$" + str(merged_fields[index])
        self.pipeline.append({
            "$addFields": {new_field: merged_fields}
        })
        return self

    def remove(self, *params):
        temp_list = list()
        for param in params:
            if isinstance(param, list):
                temp_list += param
            else:
                temp_list.append(param)
        self.pipeline.append({
            "$unset": temp_list
        })
        return self

    def join(self, doc_name, local_field, foreign_field, output_field):
        self.pipeline.append({
            "$lookup": {
                "from": doc_name,
                "localField": local_field,
                "foreignField": foreign_field,
                "as": output_field
                }
            })
        return self

    def parallelize(self, params):
        self.pipeline.append({
            "$unwind": "$" + params
        })
        return self

    def add_field(self, key, value):
        self.pipeline.append({
            "$addFields": {
                key: "$" + value
            }
        })
        return self

    def add_field_from_array(self, key, array_field, index):
        self.pipeline.append({
            "$addFields": {
                key: {"$arrayElemAt": ["$" + array_field, index]}
            }
        })
        return self

    def limit(self, max_limit):
        self.pipeline.append({
            "$limit": max_limit
        })
        return self

    def sort(self, condition):
        self.pipeline.append({
            "$sort": condition
        })
        return self

    def group(self, main_field, first_fields=None, push_fields=None, set_fields=None,
              sum_fields=None, average_fields=None, top_fields=None, max_fields=None,
              min_fields=None, count: str = None, std_deviation=None, custom_conditions=None):

        command_dict = {
            "$first": first_fields,
            "$push": push_fields,
            "$addToSet": set_fields,
            "$sum": sum_fields,
            "$avg": average_fields,
            "$top": top_fields,
            "$max": max_fields,
            "$min": min_fields,
            "$stdDevSamp": std_deviation
        }

        main_field = "$" + main_field.strip("$")
        group_def_dict = {"_id": main_field}

        if count:
            group_def_dict[count] = {"$count": {}}

        for key, value in command_dict.items():
            if value is None:
                continue

            operation_fields = list()
            new_fields = list()
            if isinstance(value, dict):
                for new_field, operation_field in value.items():
                    operation_fields.append(operation_field)
                    new_fields.append(new_field)
            elif isinstance(value, tuple):
                if 0 < len(value) < 1:
                    operation_fields.append(value[1])
                    new_fields.append(value[0])
                elif len(value) == 1:
                    operation_fields.append(value[0])
                    new_fields.append(value[0])
                else:
                    if self.log_flag:
                        logger.error(
                            "Tuple must contain at least 1, "
                            "at most 2 items to match fields."
                        )
                    continue
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        operation_fields.append(item)
                        new_fields.append(item)

                    elif isinstance(item, dict):
                        for new_field, operation_field in item.items():
                            operation_fields.append(operation_field)
                            new_fields.append(new_field)

                    else:
                        if self.log_flag:
                            logger.error(
                                "List must contain the field names, "
                                "not nested objects."
                            )
                        continue
            elif isinstance(value, str):
                operation_fields.append(value)
                new_fields.append(value)
            else:
                if self.log_flag:
                    logger.error(
                        f"The object {value}, must be in the type of the following classes; ",
                        "list, dict, tuple, or string. Recommended way is to use dictionaries.",
                        "Key of the dict. will represents the new field name to generate after group,",
                        " the value of the dict on the other hand will represents",
                        "the field name which operation will happen."
                    )
                continue

            for index in range(len(new_fields)):
                try:
                    group_def_dict[new_fields[index]] = {key: "$" + str(operation_fields[index])}
                except Exception as err:
                    if self.log_flag:
                        logger.error(err)
                    continue

        if custom_conditions:
            try:
                group_def_dict = {**group_def_dict, **custom_conditions}
            except Exception as err:
                if self.log_flag:
                    logger.error(err)

        self.pipeline.append({
            "$group": group_def_dict
        })

        return self

    def copy(self):
        temp_query_object = QueryPipeline(root_document=self.document)
        temp_query_object.pipeline = self.pipeline.copy()
        return temp_query_object

    def run(self):
        tick = time.time()
        result = self.document.objects.aggregate(
            pipeline=self.pipeline, allowDiskUse=self.disk_usage
        )
        tock = time.time()
        if self.log_flag:
            msg = f"DOCUMENT: {self.doc_name}, "
            msg += f"TIME: {tock-tick}, "
            msg += f"PIPELINE: {self.pipeline}."
            logger.info(msg)
        return result
