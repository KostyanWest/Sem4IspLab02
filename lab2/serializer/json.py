import json


def get_extentions():
    return ["json"]


def get_read_mod():
    return "r"


def get_write_mod():
    return "w"


def dumps(obj):
    return json.dumps(obj, indent=4)


def dump(obj, fp):
    fp.write(dumps(obj))


def loads(s):
    return json.loads(s)


def load(fp):
    return loads(fp.read())
