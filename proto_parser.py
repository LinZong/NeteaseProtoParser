# coding=utf-8
import struct

# Constant Definitions
HexStringMap = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
UNKNOWN_SIZE = -1
BlankSymbol = [" ", "\n", "\r", "\t"]


def is_alphabet(ch):
    a_z = range(ord('a'), ord('z'))
    A_Z = range(ord('A'), ord('Z'))
    return ord(ch) in a_z or ch in A_Z


def is_underscore(ch):
    return ch == '_'


def is_digit(ch):
    ch_ord = ord(ch)
    return ord('0') <= ch_ord <= ord('9')


def is_valid_c_style_var_name(ch, first=False):
    if first:
        return is_alphabet(ch) or is_underscore(ch)
    return is_alphabet(ch) or is_underscore(ch) or is_digit(ch)


def WrapToUnicode(original):
    return unicode(original, encoding="utf-8")


def ToHexString(data):
    result = ""
    for b in data:
        low = b & 0x0F
        high = (b >> 4) & 0x0F
        result += HexStringMap[high] + HexStringMap[low]
    return result


def ParseHexString(hex_str):
    data = []
    for x in range(0, len(hex_str), 2):
        high = int(hex_str[x], 16) << 4
        low = int(hex_str[x + 1], 16)
        data.append(low | high)
    return data


class Type(object):
    def get_size(self):
        pass

    def get_descriptor(self):
        pass

    def serialize(self, runtime_value):
        pass

    def deserialize(self, serialized_value):
        pass


class PrimitiveType(Type):
    def __init__(self, name, size):
        super(PrimitiveType, self).__init__()
        self.name = name
        self.size = size

    def get_size(self):
        return self.size

    def get_descriptor(self):
        return self.name

    def __eq__(self, o):
        if o is None:
            return False
        if id(self) == id(o):
            return True
        if not isinstance(o, PrimitiveType):
            return False
        if self.name == o.name and self.size == o.size:
            return True
        return False

    # runtime_value 是字节数组的string表示法
    # 返回字节数组的int位表示法
    def serialize(self, runtime_value):
        return [ord(x) for x in runtime_value]

    # 将字节数组int表示法转换成python内部string表示法
    def deserialize(self, serialized_value):
        return "".join([chr(x) for x in serialized_value])


class VariableSizePrimitiveType(PrimitiveType):

    def __init__(self, name, size):
        super(VariableSizePrimitiveType, self).__init__(name, size)

    def calc_size(self, runtime_value):
        # default implementation
        return self.get_size()


class CompositeType(Type):
    def __init__(self):
        super(CompositeType, self).__init__()
        self.inner_types = []

    def add_type(self, inner_type):
        self.inner_types.append(inner_type)

    def generate_type_map(self):
        m = {}
        for x in self.inner_types:
            if x in m:
                m[x] += 1
            else:
                m[x] = 1
        return m

    def get_size(self):
        return sum([x.get_size() for x in self.inner_types])

    def get_descriptor(self):
        res = []
        m = self.generate_type_map()
        for x in m.iterkeys():
            typ = x
            count = m[x]
            res.append("%s_%s" % (typ.get_descriptor(), count))
        return ":".join(res)

    def __eq__(self, o):
        if o is None:
            return False
        if id(self) == id(o):
            return True
        if not isinstance(o, CompositeType):
            return False
        m_self = self.generate_type_map()
        o_self = o.generate_type_map()
        return m_self == o_self


class ArrayType(Type):

    def __init__(self, element_type, length):
        super(ArrayType, self).__init__()
        self.element_type = element_type
        self.length = length
        self.fixed_length = length != UNKNOWN_SIZE

    def get_size(self):
        if not self.fixed_length:
            return self.fixed_length * self.element_type.get_size()
        return UNKNOWN_SIZE

    def get_descriptor(self):
        return self.element_type.get_descriptor() + "[]"

    def serialize(self, runtime_value):
        # TODO 实现，变长数组需要额外记录长度信息
        pass

    def deserialize(self, serialized_value):
        # TODO 实现反序列化
        pass


# Then we defile field

class Field(object):
    def __init__(self, typ, name, value):
        self.typ = typ
        self.name = name
        self.value = value

    def get_name(self):
        return self.name

    def get_type(self):
        return self.typ

    def get_size(self):
        if isinstance(self.typ, VariableSizePrimitiveType):
            return self.typ.calc_size(self.value)
        # Fixed-length primitive type.
        return self.typ.get_size()

    def serialize(self):
        return self.typ.serialize(self.value)

    def deserialize(self, serialized_value):
        return self.typ.deserialize(serialized_value)


class ArrayField(Field):

    # typ is array-type, value is element array
    def __init__(self, typ, name, value):
        super(ArrayField, self).__init__(typ, name, value)

    def get_length(self):
        return len(self.value)

    def get_field(self, index):
        return self.value[index]

    def get_values(self):
        return self.value

    def get_size(self):
        if isinstance(self.typ, VariableSizePrimitiveType):
            return sum([self.typ.calc_size(x) for x in self.get_values()])
        return sum([x.get_size() for x in self.get_values()])


class CompositeField(Field):
    def __init__(self, name):
        super(CompositeField, self).__init__(CompositeType(), name, None)
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)
        self.typ.add_type(field.typ)


class String(VariableSizePrimitiveType):

    def __init__(self):
        super(String, self).__init__("string", 2)

    def calc_size(self, runtime_value):
        return self.get_size() + len(WrapToUnicode(runtime_value))

    def serialize(self, runtime_value):
        str_bytes = bytearray(WrapToUnicode(runtime_value), encoding="utf-8")
        return [int(x) for x in str_bytes]

    def deserialize(self, serialized_value):
        return super(String, self).deserialize(serialized_value)


# Then we define some common primitive type here.

class Int8(PrimitiveType):
    def __init__(self):
        super(Int8, self).__init__("int8", 1)

    def serialize(self, runtime_value):
        return super(Int8, self).serialize(struct.pack("<b", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<b", super(Int8, self).deserialize(serialized_value))[0]


class UInt8(PrimitiveType):
    def __init__(self):
        super(UInt8, self).__init__("uint8", 1)

    def serialize(self, runtime_value):
        return super(UInt8, self).serialize(struct.pack("<B", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<B", super(UInt8, self).deserialize(serialized_value))[0]


class Int16(PrimitiveType):
    def __init__(self):
        super(Int16, self).__init__("int16", 2)

    def serialize(self, runtime_value):
        return super(Int16, self).serialize(struct.pack("<h", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<h", super(Int16, self).deserialize(serialized_value))[0]


class UInt16(PrimitiveType):
    def __init__(self):
        super(UInt16, self).__init__("uint16", 2)

    def serialize(self, runtime_value):
        return super(UInt16, self).serialize(struct.pack("<H", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<H", super(UInt16, self).deserialize(serialized_value))[0]


class Int32(PrimitiveType):
    def __init__(self):
        super(Int32, self).__init__("int32", 4)

    def serialize(self, runtime_value):
        return super(Int32, self).serialize(struct.pack("<i", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<i", super(Int32, self).deserialize(serialized_value))[0]


class UInt32(PrimitiveType):
    def __init__(self):
        super(UInt32, self).__init__("uint32", 4)

    def serialize(self, runtime_value):
        return super(UInt32, self).serialize(struct.pack("<I", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<I", super(UInt32, self).deserialize(serialized_value))[0]


class Float(PrimitiveType):
    def __init__(self):
        super(Float, self).__init__("float", 4)

    def serialize(self, runtime_value):
        return super(Float, self).serialize(struct.pack("<f", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<f", super(Float, self).deserialize(serialized_value))[0]


class Double(PrimitiveType):
    def __init__(self):
        super(Double, self).__init__("double", 8)

    def serialize(self, runtime_value):
        return super(Double, self).serialize(struct.pack("<d", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<d", super(Double, self).deserialize(serialized_value))[0]


class Bool(PrimitiveType):
    def __init__(self):
        super(Bool, self).__init__("bool", 1)

    def serialize(self, runtime_value):
        return super(Bool, self).serialize(struct.pack("<?", runtime_value))

    def deserialize(self, serialized_value):
        return struct.unpack("<?", super(Bool, self).deserialize(serialized_value))[0]


INT_8 = Int8()
UINT_8 = UInt8()
INT_16 = Int16()
UINT_16 = UInt16()
INT_32 = Int32()
UINT_32 = UInt32()
FLOAT = Float()
DOUBLE = Double()
BOOL = Bool()
STRING = String()

TypeNamingMap = {x.name: x for x in [INT_8, UINT_8, INT_16, UINT_16, INT_32, UINT_32, FLOAT, DOUBLE, BOOL, STRING]}


class ProtoReader(object):
    def __init__(self, proto_str):
        super(ProtoReader, self).__init__()
        self.proto_str = WrapToUnicode(proto_str)
        self.index = 0

    def advance(self, count=1):
        self.index += count

    def peek(self):
        ch = self.proto_str[self.index]
        return ch

    def peeks(self, count=1):
        ch = self.proto_str[self.index:self.index + count]
        return ch

    def read_skip_blank(self):
        while not self.reach_end():
            ch = self.read()
            if ch in BlankSymbol:
                continue
            return ch
        return ""

    def read_c_style_variable_name(self):
        name = ""
        if self.reach_end():
            raise self.error("EOF")
        ch = self.read_skip_blank()
        if not is_valid_c_style_var_name(ch, first=True):
            raise self.error("c-style variable name should be started with alphabet or underscore.")
        name += ch
        while not self.reach_end():
            ch = self.peek()
            if ch == ';':
                # 结束
                self.advance()  # 吃掉;号
                return name
            elif is_valid_c_style_var_name(ch, first=False):
                name += ch
                self.advance()
            else:
                raise self.error("not a valid char for c-style variable name: %s." % ch)

        return name

    def read_to_int(self):
        res = 0
        while not self.reach_end():
            ch = self.peek()
            if is_digit(ch):
                res = res * 10 + int(ch)
                self.advance()
            else:
                break
        return res

    def read(self):
        ch = self.peek()
        self.advance(1)
        return ch

    def reads(self, count=1):
        preview = self.peeks(count)
        self.advance(count)
        return preview

    def reach_end(self):
        return self.index >= self.length()

    def length(self):
        return len(self.proto_str)

    def error(self, msg):
        raise Exception("At {}, {}.".format(self.index, msg))


class ProtoParser(object):
    def __init__(self):
        super(ProtoParser, self).__init__()
        self.root_fields = CompositeField("root")
        self.parsing_fields_pack = []

    @staticmethod
    def parse_field_name(reader):
        return reader.read_c_style_variable_name()

    # return ok, size
    def try_parse_array_definition(self, reader):
        array_or_variable_name = reader.read_skip_blank()
        if array_or_variable_name != '[':
            reader.advance(-1)
            return False, 0
        else:
            # 数组定义
            prev_reader_index = reader.index
            array_size = reader.read_to_int()
            assert array_size >= 0
            curr_reader_index = reader.index
            if reader.read() != ']':
                self.raise_error("not closed array-size definition")
            # 如果reader的下标没动，说明根本没读到数字，是[]，所以是变长数组
            variable_arr = prev_reader_index == curr_reader_index
            return True, UNKNOWN_SIZE if variable_arr else array_size

    def parse_int(self, reader, pack):
        type_name = "i"
        type_name += reader.reads(2)
        if type_name != 'int':
            self.raise_error("expect int prefix, but %s occurred" % type_name)
        int_size = reader.read()
        if int_size == '8':
            # 断言类型为int8
            type_name += '8'
        elif int_size == '1':
            int_size += reader.read()
            if int_size != "16":
                self.raise_error("expect int16 but %s occurred." % (type_name + int_size))
            type_name += "16"
        elif int_size == '3':
            int_size += reader.read()
            if int_size != "32":
                self.raise_error("expect int32 but %s occurred." % (type_name + int_size))
            type_name += "32"
        # 现在int_size存了具体的值了
        # 接着往后读一个字符，看看会不会是数组定义
        is_array, array_size = self.try_parse_array_definition(reader)
        field_name = self.parse_field_name(reader)  # ;也被吃掉了的。
        if is_array:
            parsed_type = ArrayType(TypeNamingMap[type_name], array_size)
            return ArrayField(parsed_type, field_name, None)
        return Field(TypeNamingMap[type_name], field_name, None)

    def parse_uint(self, reader, pack):
        type_name = "u"
        type_name += reader.reads(3)
        if type_name != 'uint':
            self.raise_error("expect uint prefix, but %s occurred" % type_name)
        int_size = reader.read()
        if int_size == '8':
            # 断言类型为int8
            type_name += '8'
        elif int_size == '1':
            int_size += reader.read()
            if int_size != "16":
                self.raise_error("expect uint16 but %s occurred." % (type_name + int_size))
            type_name += "16"
        elif int_size == '3':
            int_size += reader.read()
            if int_size != "32":
                self.raise_error("expect uint32 but %s occurred." % (type_name + int_size))
            type_name += "32"
        # 现在int_size存了具体的值了
        # 接着往后读一个字符，看看会不会是数组定义
        is_array, array_size = self.try_parse_array_definition(reader)
        field_name = self.parse_field_name(reader)  # ;也被吃掉了的。
        if is_array:
            parsed_type = ArrayType(TypeNamingMap[type_name], array_size)
            return ArrayField(parsed_type, field_name, None)
        return Field(TypeNamingMap[type_name], field_name, None)

    def parse_float(self, reader, pack):
        return self.parse_typed_field(reader, "float")

    def parse_double(self, reader, pack):
        return self.parse_typed_field(reader, "double")

    def parse_bool(self, reader, pack):
        return self.parse_typed_field(reader, "bool")

    def parse_string(self, reader, pack):
        return self.parse_typed_field(reader, "string")

    def parse_typed_field(self, reader, expected_full_name):
        type_name = expected_full_name[0:1]
        type_name += reader.reads(len(expected_full_name) - 1)
        if type_name != expected_full_name:
            self.raise_error("expect %s, but %s occurred" % (expected_full_name, type_name))
        # 现在int_size存了具体的值了
        # 接着往后读一个字符，看看会不会是数组定义
        is_array, array_size = self.try_parse_array_definition(reader)
        field_name = self.parse_field_name(reader)  # ;也被吃掉了的。
        if is_array:
            parsed_type = ArrayType(TypeNamingMap[type_name], array_size)
            return ArrayField(parsed_type, field_name, None)
        return Field(TypeNamingMap[type_name], field_name, None)

    def parse_into(self, reader, pack):
        while not reader.reach_end():
            ch = reader.read_skip_blank()
            if ch == 'i':
                pack.add_field(self.parse_int(reader, pack))
                continue
            elif ch == 'u':
                pack.add_field(self.parse_uint(reader, pack))
                continue
            elif ch == 'f':
                pack.add_field(self.parse_float(reader, pack))
                continue
            elif ch == 'd':
                pack.add_field(self.parse_double(reader, pack))
                continue
            elif ch == 'b':
                pack.add_field(self.parse_bool(reader, pack))
                continue
            elif ch == 's':
                pack.add_field(self.parse_string(reader, pack))
                continue
            elif ch == '{':
                sub_field = CompositeField("stub-name")
                # 入parsing stack
                self.parsing_fields_pack.append(sub_field)
                self.parse_into(reader, sub_field)
                continue
            elif ch == '}':
                # pack结束, 对于子CompositeField, 需要额外处理，加上名字。
                if len(self.parsing_fields_pack) > 1:
                    is_array, size = self.try_parse_array_definition(reader)
                    field_name = self.parse_field_name(reader)
                    # {时入, }时出
                    self.parsing_fields_pack = self.parsing_fields_pack[:-1]
                    if is_array:
                        wrap_field = ArrayField(ArrayType(pack.typ, size), field_name, None)
                        # 将栈顶替换为包装后的数组类型
                        self.parsing_fields_pack[-1:][0].add_field(wrap_field)
                    else:
                        pack.name = field_name
                        self.parsing_fields_pack[-1:][0].add_field(pack)
                return
            else:
                self.raise_error("invalid ch %s at %s" % (ch, reader.index - 1))

    def parse(self, proto_text):
        reader = ProtoReader(proto_text)
        while not reader.reach_end():
            ch = reader.read_skip_blank()
            if ch == '{':
                self.parsing_fields_pack.append(self.root_fields)
                self.parse_into(reader, self.root_fields)
                self.parsing_fields_pack = self.parsing_fields_pack[:-1]
            else:
                self.raise_error("invalid char %s at %s" % (ch, reader.index - 1))
        pass

    def raise_error(self, msg):
        raise Exception("PARSER ERROR: " + msg)