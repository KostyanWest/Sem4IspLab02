import builtins
import inspect
import types
from importlib import import_module


_loaded = {}

_moduleattrs = ("__name__", "__doc__")

_funcattrs1 = ("__code__", "__globals__", "__name__", "__defaults__", "__closure__")

_funcattrs2 = (
    "__qualname__",
    "__doc__",
    "__dict__",
    "__module__",
    "__kwdefaults__",
    "__annotations__",
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

_builtin = {
    **{
        str(getattr(builtins, key)): getattr(builtins, key)
        for key in dir(builtins)
        if type(getattr(builtins, key)) is type
    },
    **{
        str(getattr(types, key)): getattr(types, key)
        for key in dir(types)
        if type(getattr(types, key)) is type
    },
    str(type(Ellipsis)): type(Ellipsis),
    str(type(NotImplemented)): type(NotImplemented),
}


def _load_id(id_str):
    return int(id_str.rpartition(" at ")[2], 0)


def _load_id_data(id_str):
    if id_str.startswith("<"):
        return (_builtin[id_str], True)
    else:
        id_int = _load_id(id_str)
        return _loaded.get(id_int, (id_int, False))


def _load_dict(shell, dct):
    for pair in dct["__value__"]:
        shell[_load_obj(pair[0])] = _load_obj(pair[1])


def _load_mapping(shell, dct):
    tmp = {}
    _load_dict(tmp, dct)
    return types.MappingProxyType(tmp)


def _load_globals():
    from ... import __name__ as border

    for frame in inspect.stack():
        if not frame[1].startswith(border):
            return frame[0].f_globals


def _load_func(shell, dct):
    g = _load_globals()
    tmp = {key: _load_obj(dct[key]) for key in _funcattrs1}
    g.update(tmp["__globals__"])
    tmp["__globals__"] = g

    func = types.FunctionType(*tmp.values())
    for key in _funcattrs2:
        setattr(func, key, _load_obj(dct[key]))

    return func


_how2shell = {
    # simple
    type(None):           lambda cls, dct: None,
    type(Ellipsis):       lambda cls, dct: Ellipsis,
    type(NotImplemented): lambda cls, dct: NotImplemented,
    object:               lambda cls, dct: object(),

    # numeric
    bool:    lambda cls, dct: cls(dct["__value__"]),
    int:     lambda cls, dct: cls(dct["__value__"]),
    float:   lambda cls, dct: cls(dct["__value__"]),
    complex: lambda cls, dct: cls(dct["__value__"]),

    # sequence
    str:     lambda cls, dct: cls(dct["__value__"]),
    range:   lambda cls, dct: cls(*dct["__value__"]),

    # binary
    bytes:      lambda cls, dct: cls.fromhex(dct["__value__"]),
    bytearray:  lambda cls, dct: cls.fromhex(dct["__value__"]),
    memoryview: lambda cls, dct: cls(bytes()),

    # mappingdict
    types.MappingProxyType: lambda cls, dct: cls({}),

    # method
    types.MethodType:   lambda cls, dct: cls(
        _load_shell(dct["__func__"]),
        _load_shell(dct["__self__"]),
    ),
    types.FunctionType: lambda cls, dct: _load_id,
    types.CodeType:     lambda cls, dct: cls(
        *(_load_shell(dct[key]) for key in _codeattrs)
    ),
    # other
    types.ModuleType:   lambda cls, dct: cls(
        *(_load_shell(dct[key]) for key in _moduleattrs)
    ),
}

_how2load = {
    # sequence
    list:       lambda shell, dct: shell.extend(_load_obj(obj) for obj in dct["__value__"]),
    tuple:      lambda shell, dct: tuple(_load_obj(obj) for obj in dct["__value__"]),

    # binary
    memoryview: lambda shell, dct: memoryview(_load_obj(dct["__value__"])),

    # set
    set:        lambda shell, dct: shell.update(_load_obj(obj) for obj in dct["__value__"]),
    frozenset:  lambda shell, dct: frozenset(_load_obj(obj) for obj in dct["__value__"]),

    # mapping
    dict: _load_dict,
    types.MappingProxyType: _load_mapping,

    # methond
    types.MethodType:   lambda shell, dct: types.MethodType(
        _load_obj(dct["__func__"]),
        _load_obj(dct["__self__"]),
    ),
    types.FunctionType: _load_func,
    types.CellType:     lambda shell, dct: types.CellType(_load_obj(dct["__value__"])),
    types.ModuleType:   lambda shell, dct: import_module(dct["__name__"]),
}


def _load_shell(obj2load):
    if type(obj2load) is list:
        return tuple(_load_shell(element) for element in obj2load)

    if not type(obj2load) is dict:
        return obj2load

    loaded_shell = _load_id_data(obj2load["__id__"])[0]
    if not type(loaded_shell) is int:
        return loaded_shell

    class_shell = _load_shell(obj2load["__class__"])
    if "__bases__" in obj2load:
        shell = class_shell(
            obj2load["__name__"],
            _load_shell(obj2load["__bases__"]),
            {"__slots__": obj2load["__slots__"]} if "__slots__" in obj2load else {},
        )
    else:
        shell = _how2shell.get(class_shell, lambda cls, dct: cls())(
            class_shell, obj2load
        )
    _loaded[loaded_shell] = (shell, False)

    for value in obj2load.values():
        _load_shell(value)
    return shell


def _load_class(shell, dict2load):
    _loaded[_load_id(dict2load["__id__"])] = (shell, True)
    _load_obj(dict2load["__class__"])
    _load_obj(dict2load["__bases__"])

    for key, value in _load_obj(dict2load["__dict__"]).items():
        setattr(shell, key, value)

    return shell


def _load_obj(obj2load):
    if type(obj2load) is list:
        return tuple(_load_obj(element) for element in obj2load)

    if not type(obj2load) is dict:
        return obj2load

    shell, is_ready = _load_id_data(obj2load["__id__"])
    if is_ready:
        return shell

    _load_obj(obj2load["__class__"])

    if "__bases__" in obj2load:
        return _load_class(shell, obj2load)

    obj = _how2load.get(type(shell), lambda shell, dct: None)(shell, obj2load)
    if obj is None:
        obj = shell
    _loaded[_load_id(obj2load["__id__"])] = (obj, True)

    if "__dict__" in obj2load:
        setattr(obj, "__dict__", _load_obj(obj2load["__dict__"]))

    if "__slots__" in obj2load:
        for key, value in _load_obj(obj2load["__slots__"]).items():
            setattr(obj, key, value)

    return obj


def load(obj2load):
    _loaded.clear()
    _load_shell(obj2load)
    return _load_obj(obj2load)
