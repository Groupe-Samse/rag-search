import json

ENCODING = "utf8"

def read_json_return_result_tab(file_path, field="hits"):
    result = []
    with open(file_path, encoding=ENCODING) as data_file:
        data = json.load(data_file)
        for i in data[field]:
            result.append(i)
        return result
