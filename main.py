# coding=utf-8
# Press the green button in the gutter to run the script.
from proto_parser import *

if __name__ == '__main__':
    with open("a1.proto", "r") as f:
        text = "".join(f.readlines())
        parser = ProtoParser()
        parser.parse(text)
        print parser
