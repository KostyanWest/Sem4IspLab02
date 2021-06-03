import pickle


def get_extentions():
    return ["pickle"]


def get_read_mod():
    return "br"


def get_write_mod():
    return "bw"


def dumps(obj):
    return pickle.dumps(obj)


def dump(obj, fp):
    fp.write(dumps(obj))


def loads(s):
    return pickle.loads(s)


def load(fp):
    return loads(fp.read())
