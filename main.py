# coding=utf-8
# Press the green button in the gutter to run the script.
from proto_parser import *

if __name__ == '__main__':
	wwj = "伍文杰"
	print STRING.serialize(wwj)
	wwj = bytearray(unicode("伍文杰", encoding="utf-8"), encoding="utf-8")
	print [x for x in wwj]
    # with open("a1.proto", "r") as f:
    #     text = "".join(f.readlines())
    #     parser = ProtoParser()
    #     parser.parse(text)
    #     print parser
