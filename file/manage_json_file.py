import json
import re

ENCODING = "utf8"
PATTERN = r'<[^>]+>'


def __aggregate_fields(hit, ignore_field, new_field):
    """
    Aggregate fields in a new field

    :param hit: item to aggregate
    :param ignore_field: fields to ignore
    :param new_field: new field name
    :return: hit with new field
    """
    separator = ' '
    hit[new_field] = separator.join([value for key, value in hit.items() if key not in ignore_field])
    return hit


def __read_json_return_from_result_list(file_path):
    """
    Read json file from path and return the result list

    :param file_path: file path
    :return: result list
    """
    result = []
    with open(file_path, encoding=ENCODING) as data_file:
        data = json.load(data_file)
        for i in data:
            result.append(i)
        return result


def __clean_json(json_data):
    """
    Clean json data recursively

    :param json_data: json data
    :return: cleaned json data
    """
    if isinstance(json_data, dict):
        return {key: __clean_json(value) for key, value in json_data.items()}
    elif isinstance(json_data, list):
        return [__clean_json(item) for item in json_data]
    else:
        if isinstance(json_data, str):
            return re.sub(PATTERN, '', json_data)
        return json_data


def read_clean_and_aggregate_tab(path):
    """
    Read, clean and aggregate json file

    :param path: file path
    :return:
    """
    json_clean = __clean_json(__read_json_return_from_result_list(path))

    for hit in json_clean:
        __aggregate_fields(hit["_source"], ["_id", "_index", "_score"], "text")

    return json_clean
