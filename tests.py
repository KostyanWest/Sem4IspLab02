import logging
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

import unittest
import lab2
import types


class ValueTests(unittest.TestCase):
    def tearDown(self):
        serialized = lab2.dumps(self.subject, "json")
        self.restored = lab2.loads(serialized, "json")
        self.assertTrue(self.restored == self.subject)
        del self.subject
        del self.restored


    def test_none(self):
        self.subject = None

    def test_ellipsis(self):
        self.subject = Ellipsis

    def test_notimplemented(self):
        self.subject = NotImplemented


    def test_false(self):
        self.subject = False

    def test_true(self):
        self.subject = True

    def test_int(self):
        self.subject = -62384981612483286682487

    def test_float(self):
        self.subject = 22 / 7

    def test_complex(self):
        self.subject = complex(-4214, 0.73278)


    def test_str(self):
        self.subject = "Sample Text"

    def test_list(self):
        self.subject = [10, 30, 20]

    def test_tuple(self):
        self.subject = (10, 30, 20)

    def test_range(self):
        self.subject = range(10, 30, 20)


    def test_bytes(self):
        self.subject = bytes.fromhex("02 ad 73 ff")

    def test_bytearray(self):
        self.subject = bytearray.fromhex("7d 10 37 00")


    def test_set(self):
        self.subject = {10, 30, 20}

    def test_frozenset(self):
        self.subject = frozenset({10, 30, 20})


    def test_dict(self):
        self.subject = {10: 20, 30: 40}

    def test_mappingproxy(self):
        self.subject = types.MappingProxyType({10: 20, 30: 40})


class WrapperTests(unittest.TestCase):
    def tearDown(self):
        serialized = lab2.dumps(self.subject, "json")
        self.restored = lab2.loads(serialized, "json")
        self.assertTrue(self.restored.obj == self.subject.obj)
        del self.subject
        del self.restored

    def test_memoryview(self):
        self.subject = memoryview(bytearray.fromhex("39 ab 73 35"))


class MethodCls():
    def my_method(self):
        return self
    var = "variable"

class FunctionTests(unittest.TestCase):
    def setUp(self):
        self.globals_backup = {}
        self.globals_backup.update(globals())

    def tearDown(self):
        globals().clear()
        globals().update(self.globals_backup)

    def compare_closure(self, obj1, obj2):
        if obj1 == None and obj2 == None:
            return True
        for i in range(len(obj1)):
            if not obj1[i] == obj2[i]:
                return False
        else:
            return True

    def compare(self, obj1, obj2, attrs):
        for attr in attrs:
            with self.subTest(attr=attr):
                if attr == "__closure__":
                    self.compare_closure(obj1.__closure__, obj2.__closure__)
                elif attr == "__module__":
                    pass
                else:
                    self.assertTrue(getattr(obj1, attr) == getattr(obj2, attr))

    def foo():
        pass

    def f_globals():
        return math.sin(x)

    def indent(x):
        def closure(y):
            return x + y
        return closure

    def test_foo_code(self):
        subject = FunctionTests.foo.__code__
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._codeattrs)
        #self.assertTrue(restored == subject)

    def test_foo_func(self):
        subject = FunctionTests.foo
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        #self.assertTrue(restored == subject)

    def test_globals_func(self):
        subject = FunctionTests.f_globals
        import math
        globals()["math"] = math
        globals()["x"] = 5
        del math
        s_result = subject()
        serialized = lab2.dumps(subject, "json")
        del globals()["math"]
        del globals()["x"]

        restored = lab2.loads(serialized, "json")
        r_result = restored()
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.assertTrue(s_result == r_result)

    def test_closure_func(self):
        subject = FunctionTests.indent(5)
        s_result = subject(10)
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        r_result = restored(10)
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.assertTrue(s_result == r_result)


    def test_indent_func(self):
        subject = FunctionTests.indent
        s_result = subject(5)
        ss_result = s_result(10)
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        r_result = restored(5)
        rr_result = r_result(10)
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.compare(s_result, r_result, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.assertTrue(ss_result == rr_result)

    def test_lambda(self):
        subject = lambda x: x * 10
        s_result = subject(5)	
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        r_result = restored(5)
        self.compare(subject, restored, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.assertTrue(s_result == r_result)

    def test_method(self):
        subject = MethodCls().my_method
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare(subject.__func__, restored.__func__, lab2.serializer.serialize_tools.dump_tool._funcattrs)
        self.assertTrue(restored() is restored.__self__)


class SimpleCls():
    pass

class ContainerCls():
    none = None
    bool = True
    int = 1251
    float = 22/7
    str = "string"
    tuple = tuple("tuple")
    list = list("list")
    dict = {"d": "i", "c": "t"}

class SlotsCls():
    __slots__ = ("a", "b", "c")

class MetaCls(type):
    pass

class ParentCls(metaclass=MetaCls):
    pass

class ChildCls(ParentCls, ContainerCls, metaclass=MetaCls):
    pass

class ClassTests(unittest.TestCase):
    def compare_vars(self, obj1, obj2):
        for var in vars(obj2):
            if var not in ("__dict__", "__weakref__", "__module__"):
                with self.subTest(var=var):
                    self.assertTrue(getattr(obj1, var) == getattr(obj2, var))

    def compare_slots(self, obj1, obj2):
        for var in type(obj2).__slots__:
            with self.subTest(var=var):
                if hasattr(obj1, var) and hasattr(obj2, var):
                    self.assertTrue(getattr(obj1, var) == getattr(obj2, var))
                else:
                    self.assertTrue(hasattr(obj1, var) == hasattr(obj2, var))

    def test_simple_cls(self):
        subject = SimpleCls
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.assertTrue(restored.__name__ == subject.__name__)

    def test_container_cls(self):
        subject = ContainerCls
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare_vars(restored, subject)
        self.assertTrue(restored.__name__ == subject.__name__)

    def test_container_obj(self):
        subject = ContainerCls()
        subject.a = "orevrride"
        subject.d = "new var"
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare_vars(restored, subject)
        self.compare_vars(type(restored), type(subject))
        self.assertTrue((type(restored).__name__) == type(subject).__name__)

    def test_slots(self):
        subject = SlotsCls()
        subject.a = "var a"
        subject.b = "var b"
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.compare_slots(restored, subject)
        self.assertTrue((type(restored).__name__) == type(subject).__name__)

    def test_inheritance(self):
        subject = ChildCls
        serialized = lab2.dumps(subject, "json")

        restored = lab2.loads(serialized, "json")
        self.assertTrue(restored.__name__ == subject.__name__)
        self.assertTrue(restored.__bases__[0].__name__ == subject.__bases__[0].__name__)
        self.assertTrue(restored.__bases__[1].__name__ == subject.__bases__[1].__name__)
        self.assertTrue((type(restored).__name__) == type(subject).__name__)
        

class FileTests(unittest.TestCase):
    def test_file(self):
        subject = ContainerCls
        with open("test_file.json", "w") as fp:
            lab2.dump(subject, fp)
        with open("test_file.json", "r") as fp:
            restored = lab2.load(fp)
        ClassTests.compare_vars(self, restored, subject)

    def test_convert_s(self):
        subject = ContainerCls
        from itertools import permutations as perms

        for perm in perms(lab2.get_langs(), 2):
            with self.subTest(perm=perm):
                serialized = lab2.dumps(subject, perm[0])
                serialized = lab2.convert_s(serialized, perm[0], perm[1])
                restored = lab2.loads(serialized, perm[1])
                ClassTests.compare_vars(self, restored, subject)

    def test_convert_f(self):
        subject = ContainerCls
        from lab2.__main__ import main
        main(["test_file.json", "test_file.yaml"])
        with open("test_file.yaml", "r") as fp:
            restored = lab2.load(fp)
        ClassTests.compare_vars(self, restored, subject)


if __name__ == "__main__":
    unittest.main()
