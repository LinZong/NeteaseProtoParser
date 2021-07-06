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

a4_test = {
    "skills": (
        {"id": 1, "level": 2, "name": "3", "props": (1, 2, 3)},
        {"id": 4, "level": 2, "name": "3", "props": (4, 5, 6)}),
    "items": ({"id": 10, "number": 11},)
}


def test1():
    wwj = "伍文杰+苏希强烔"
    byte_arr = STRING.serialize(wwj)
    reader = ByteArrayInputStream(byte_arr)
    print STRING.deserialize(reader)


def test2():
    parser = ProtoParser()
    parser.buildDesc("1_8.proto")
    print parser
    # a4 = parser.dumps(a4_test)
    # a4_rec = parser.loads(a4)
    # print_dict(a4_rec)
    # dump_hex_str = parser.dumps(test_obj)
    # print dump_hex_str
    # print "判断是否正确"
    # assert dump_hex_str == "0900e9aaa8e7b2bee781b5a25d4f00000200a35d4f00fbf9930e0080064300000000ae47bb411500e9aaa8e7b2bee781b5e79a84e5b08fe58fafe788b101000200"
    # recover_obj = parser.loads(dump_hex_str)
    # print_dict(test_obj)
    # print_dict(recover_obj)


def test3():
    china = "中国"
    print len(china)


def case_convert():
    value = """
    {int8 i;}@#$%^&{\n  string msg;  \n  bool flag;\n  int32 n;\n  uint32 un;\n  uint16 um;\n  int16 m;\n  int8 c;\n  uint8 uc;\n  float x;\n  double y;\n  string Chinease;    \n  string empty;\n}@#$%^&{  \n  uint32[] friends;double[3]pos;\n  string[] skills; float[]angle;\n}@#$%^&{\n   string name;    \n
    """
    print value


if __name__ == '__main__':
    test2()
    test3()
