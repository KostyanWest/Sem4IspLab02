import yaml


def get_extentions():
    return ["yaml", "yml"]


def get_read_mod():
    return "r"


def get_write_mod():
    return "w"


def dumps(obj):
    return yaml.dump(obj)


def dump(obj, fp):
    fp.write(dumps(obj))


def loads(s):
    return yaml.safe_load(s)


def load(fp):
    return loads(fp.read())
