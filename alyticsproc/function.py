import json


def nii_function(json_str):
    data = json.loads(json_str)
    res = {'result': sum((int(d['a']) + int(d['b']) for d in data))}
    return json.dumps(res)
