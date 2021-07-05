# coding=utf-8
# Press the green button in the gutter to run the script.
from proto_parser import *

if __name__ == '__main__':
    wwj = "伍文杰+苏希强烔"
    byte_arr = STRING.serialize(wwj)
    reader = ByteArrayInputStream(byte_arr)
    print STRING.deserialize(reader)
