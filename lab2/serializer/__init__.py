from .serialize_tools import *
from . import json
from . import pickle


_langs = {}

for module in [json, pickle]:
    for ext in set(map(str.lower, module.get_extentions())):
       if not _langs.setdefault(ext, module) is module:
           raise ValueError("Both '{}' and '{}' uses '{}' extention".format(_langs[ext].__name__,
                                                                            module.__name__,
                                                                            ext))


def create_serializer(lang):
    try:
        return _langs[lang]
    except KeyError:
        raise ValueError("The lang '{}' is not supported".format(lang))


def get_langs():
    return list(_langs)
