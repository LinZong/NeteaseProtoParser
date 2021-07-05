# coding=utf-8
# Press the green button in the gutter to run the script.
from proto_parser import *
import json


def print_dict(d):
    print json.dumps(d, encoding="utf-8", ensure_ascii=False)


test_obj = {
    "name": "骨精灵",
    "id": 5201314,
    "married": False,
    "friends": (5201315, 244578811),
    "position": (134.5, 0.0, 23.41),
    "pet": {
        "name": "骨精灵的小可爱",
        "skill": (
            {"id": 1}, {"id": 2}
        )
    }
}

sample_proto_obj = {
    "a": "hello",
    "b": (12, 64, 1025),
    "c": (12.5, -33.4),
    "f": True
}


def test1():
    wwj = "伍文杰+苏希强烔"
    byte_arr = STRING.serialize(wwj)
    reader = ByteArrayInputStream(byte_arr)
    print STRING.deserialize(reader)


def test2():
    with open("a.proto", "r") as f:
        content = "".join(f.readlines())
        parser = ProtoParser()
        parser.parse(content)
        print parser
        dump_hex_str = parser.dumps(test_obj)
        print dump_hex_str
        recover_obj = parser.loads(dump_hex_str)
        print_dict(test_obj)
        print_dict(recover_obj)


if __name__ == '__main__':
    test2()
