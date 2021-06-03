import builtins
import inspect
import types
import logging


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


_dumped = []

_moduleattrs = ("__name__", "__doc__")

_funcattrs = (
    "__name__",
    "__qualname__",
    "__doc__",
    "__dict__",
    "__module__",
    "__closure__",
    "__defaults__",
    "__kwdefaults__",
    "__annotations__",
    "__code__",
)

_codeattrs = (
    "co_argcount",
    "co_posonlyargcount",
    "co_kwonlyargcount",
    "co_nlocals",
    "co_stacksize",
    "co_flags",
    "co_code",
    "co_consts",
    "co_names",
    "co_varnames",
    "co_filename",
    "co_name",
    "co_firstlineno",
    "co_lnotab",
    "co_freevars",
    "co_cellvars",
)

_builtin = (
    *(
        getattr(builtins, key)
        for key in dir(builtins)
        if type(getattr(builtins, key)) is type
    ),
    *(getattr(types, key) for key in dir(types) if type(getattr(types, key)) is type),
    type(Ellipsis),
    type(NotImplemented),
)


def _dump_none(obj, dct=None):
    pass


def _dump_mapping(dct):
    tmp = []
    for key in dct:
        try:
            tmp.append([_dump_obj(key), _dump_obj(dct[key])])
        except TypeError as error:
            logging.warning(
                f"Key <{str(key)}> in <{_dump_rich_id(dct)}> was skipped because of {error}"
            )
    return tmp


def _dump_id(obj):
    return hex(id(obj))


def _dump_rich_id(obj):
    if hasattr(obj, "__name__"):
        string = "'" + obj.__name__ + "'"
    else:
        string = "instance"
    string += " of '" + type(obj).__name__
    string += "' at " + _dump_id(obj)
    return string


def _dump_value(how2dump):
    return lambda obj, dct: dct.update({"__value__": _dump_obj(how2dump(obj))})


def _dump_specattrs(specattrs):
    return lambda obj, dct: dct.update(
        {attr: _dump_obj(getattr(obj, attr)) for attr in specattrs}
    )


def _dump_globals(func, dct):
    def dump_globals(code):
        g.extend(code.co_names)
        for const in code.co_consts:
            if type(const) is types.CodeType:
                dump_globals(const)

    g = []
    dump_globals(func.__code__)
    g_dct = {var: func.__globals__[var] for var in func.__globals__ if var in g}
    dct["__globals__"] = _dump_obj(g_dct)


def _dump_combine(*funcs):
    return lambda obj, dct: [func(obj, dct) for func in funcs]


_supported = {
    # simple
    type(None): _dump_none,
    type(Ellipsis): _dump_none,
    type(NotImplemented): _dump_none,
    object: _dump_none,
    # numeric
    bool: _dump_value(lambda obj: str(obj)),
    int: _dump_value(lambda obj: str(obj)),
    float: _dump_value(lambda obj: str(obj)),
    complex: _dump_value(lambda obj: str(obj)),
    # sequence
    str: _dump_value(lambda obj: obj),
    list: _dump_value(lambda obj: tuple(obj)),
    tuple: _dump_value(lambda obj: obj),
    range: _dump_value(lambda obj: (obj.start, obj.stop, obj.step)),
    # binary
    bytes: _dump_value(lambda obj: bytes.hex(obj, " ", 1)),
    bytearray: _dump_value(lambda obj: bytearray.hex(obj, " ", 1)),
    memoryview: _dump_value(lambda obj: obj.obj),
    # set
    set: _dump_value(lambda obj: tuple(obj)),
    frozenset: _dump_value(lambda obj: tuple(obj)),
    # mapping
    dict: lambda obj, dct: dct.update({"__value__": _dump_mapping(obj)}),
    types.MappingProxyType: lambda obj, dct: dct.update(
        {"__value__": _dump_mapping(obj)}
    ),
    # method
    types.MethodType: lambda obj, dct: dct.update(
        {
            "__func__": _dump_obj(obj.__func__),
            "__self__": _dump_obj(obj.__self__),
        }
    ),
    types.FunctionType: _dump_combine(_dump_specattrs(_funcattrs), _dump_globals),
    types.CodeType: _dump_specattrs(_codeattrs),
    types.CellType: _dump_value(lambda obj: obj.cell_contents),
    # other
    types.ModuleType: _dump_specattrs(_moduleattrs),
}


def _dump_as_list(collection):
    tmp = []
    for obj in collection:
        try:
            tmp.append(_dump_obj(obj))
        except TypeError as error:
            logging.warning(f"<{_dump_rich_id(obj)}> was skipped because of {error}")
    return tmp


def _dump_obj(obj):
    def _dump_class(cls):
        if id(cls) in _dumped:
            return {"__id__": _dump_rich_id(cls)}

        nonlocal obj, obj_dict
        if cls in _builtin:
            if not obj_dict is None:
                if cls in _supported:
                    _supported[cls](obj, obj_dict)
                else:
                    raise TypeError(f"<{_dump_rich_id(obj)}> has unsupported type")
            return {"__id__": str(cls)}

        return _dump_custom(cls)

    def _dump_custom(cls):
        _dumped.append(id(cls))
        dict2dump = {"__id__": _dump_id(cls)}
        dict2dump["__class__"] = _dump_obj(type(cls))
        dict2dump["__name__"] = getattr(cls, "__name__")

        bases_list = []
        for base in getattr(cls, "__bases__"):
            bases_list.append(_dump_class(base))
        dict2dump["__bases__"] = bases_list

        cls_dict = getattr(cls, "__dict__")
        dict2dump["__dict__"] = _dump_obj(cls_dict)

        if not obj_dict is None:
            if "__slots__" in cls_dict:
                slots = {}
                for attr in cls_dict["__slots__"]:
                    if hasattr(obj, attr):
                        slots[attr] = getattr(obj, attr)
                obj_dict.setdefault("__slots__", {}).update(slots)
            elif "__dict__" not in obj_dict:
                if hasattr(obj, "__dict__"):
                    obj_dict["__dict__"] = _dump_obj(getattr(obj, "__dict__"))

        return dict2dump

    if type(obj) is tuple:
        return _dump_as_list(obj)
    if type(obj) in (type(None), bool, int, float, str):
        return obj

    if isinstance(obj, type):
        obj_dict = None
        return _dump_class(obj)

    if id(obj) in _dumped:
        return {"__id__": _dump_rich_id(obj)}

    _dumped.append(id(obj))
    obj_dict = {"__id__": _dump_id(obj), "__class__": None}
    obj_dict["__class__"] = _dump_class(type(obj))
    if "__slots__" in obj_dict:
        obj_dict["__slots__"] = _dump_obj(obj_dict["__slots__"])
    return obj_dict


def dump(obj):
    _dumped.clear()
    return _dump_obj(obj)
