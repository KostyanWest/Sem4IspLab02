"""Lab2 -- Serialization tool

A module provides functions to dump and load objects of any custom
classes and some built-in classes using popular markup languages.

Call 'get_langs' function to see the list of supported markup languages.

The module can convert files from one markup language to another.
For that purpose the module can be used as console utility.
"""

from . import serializer


def get_langs():
    """Returns the list of supported markup languages."""

    return serializer.get_langs()


def get_serializer(lang="", filename=""):
    """Returns the serializer capable to deal with simple objects.

    Use 'lang' arg to specify markup language.
    Leave empty string to specify markup language
    from file extention.
    """

    if lang == "":
        lang = filename.rpartition(".")[2]
    return serializer.create_serializer(lang.lower())


def dumps(obj, lang):
    """Converts object to string and returns it.

    Use 'lang' arg to specify markup language.
    """

    dumper = get_serializer(lang)
    simple = serializer.dump(obj)
    return dumper.dumps(simple)


def dump(obj, fp, lang=""):
    """Converts object to string and write it to file.

    Use 'lang' arg to override markup language.
    """

    dumper = get_serializer(lang, fp.name)
    simple = serializer.dump(obj)
    return dumper.dump(simple, fp)


def loads(s, lang):
    """Converts string to object and returns it.

    Use 'lang' arg to specify markup language.
    """

    loader = get_serializer(lang)
    simple = loader.loads(s)
    return serializer.load(simple)


def load(fp, lang=""):
    """Converts string from file to object and returns it.

    Use 'lang' arg to override markup language.
    """

    loader = get_serializer(lang, fp.name)
    simple = loader.load(fp)
    return serializer.load(simple)


def convert_s(s, ilang, olang):
    """Converts serialized data from one markup language to another.
    Returns new string containig converted data.

    Use 'ilang' and 'olang' args to specify markup language for
    source and target strings.
    """

    loader = get_serializer(ilang)
    dumper = get_serializer(olang)

    if loader is dumper:
        return s
    else:
        return dumper.dumps(loader.loads(s))


def convert_f(input, output, ilang="", olang=""):
    """Converts serialized data from one markup language to another.
    Creates new file containig converted data.

    Use 'ilang' and 'olang' args to override markup language for
    source and target files.
    """

    loader = get_serializer(ilang, input)
    read_mod = loader.get_read_mod()

    dumper = get_serializer(olang, output)
    write_mod = dumper.get_write_mod()

    if loader is dumper:
        return

    with open(input, read_mod) as fp:
        loaded_data = loader.load(fp)

    with open(output, write_mod) as fp:
        dumper.dump(loaded_data, fp)
