import json


def nii_function(json_str):
    data = json.loads(json_str)
    return {'result': sum((int(d['a']) + int(d['b']) for d in data))}
