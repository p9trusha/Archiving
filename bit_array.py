class BitArray():
    def __init__(self, input_data=None, mode=None, length=None):
        self.bits = []
        if mode == "str":
            self.bits = self.bytes_to_bits(bytes(input_data))
        elif mode == "b":
            self.bits = self.bytes_to_bits(input_data)
        elif mode == "int":
            self.bits = self.bit_str_to_bits(bin(input_data)[2:], length)
        elif mode == "bit_str":
            self.bits = self.bit_str_to_bits(input_data, length)
        elif mode == "bit_int":
            self.bits = list(map(lambda x: bool(x), input_data))
        elif mode == "bit_arr":
            self.bits = input_data

    def __eq__(self, other):
        return self.bits == other.bits

    def __getitem__(self, item):
        if isinstance(item, slice):
            return BitArray(self.bits[item.start:item.stop:item.step], mode="bit_arr")
        return self.bits[item]

    def __add__(self, other):
        if isinstance(other, BitArray):
            return BitArray(self.bits + other.bits, mode="bit_arr")
        return BitArray(self.bits + other, mode="bit_arr")

    def __iadd__(self, other):
        if isinstance(other, BitArray):
            self.bits += other.bits
        elif isinstance(other, int):
            self.bits += self.bit_str_to_bits(bin(other)[2:], None)
        elif isinstance(other, list):
            self.bits += other
        return self

    def __mul__(self, other):
        return self.bits * other

    def __len__(self):
        return len(self.bits)

    def __str__(self):
        return ''.join(list(map(lambda x: str(int(x)), self.bits)))

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def bytes_to_bits(bts):
        bits = []
        for i in range(len(bts)):
            bits += list(map(lambda x: bool(int(x)), f"{bts[i]:08b}"))
        return bits

    @staticmethod
    def bit_str_to_bits(bit_str, length):
        if length is None:
            length = len(bit_str)
        return [False] * (length - len(bit_str)) + list(map(lambda x: bool(int(x)), bit_str))

    def append0(self):
        self.bits += [False]

    def append1(self):
        self.bits += [True]

    def add1(self):
        i = len(self.bits) - 1
        while i >= 0 and self.bits[i] == True:
            i -= 1
        if i == -1:
            self.bits = [True] + [False] * len(self.bits)
        else:
            self.bits = self.bits[:i] + [True] + [False] * (len(self.bits) - i - 1)
        return self

    def to_bytearray(self, without_amount_of_extra_bits=False):
        bts = bytearray()
        if not without_amount_of_extra_bits:
            bts.append(len(self.bits) % 8)
        for i in range(0, len(self.bits) // 8):
            byte = 0
            for j in range(8):
                byte += int(self.bits[i * 8 + j]) * (2 ** (8 - j - 1))
            bts.append(byte)
        if len(self.bits) % 8 != 0:
            byte = 0
            for j in range(len(self.bits) % 8):
                byte += int(self.bits[len(self.bits) // 8 * 8 + j]) * 2 ** (7 - j)
            bts.append(byte)
        return bts

    def copy(self):
        return BitArray(self.bits, "bit_arr")



def int_from_binary(binary_data):
    if type(binary_data) == int:
        return binary_data
    if type(binary_data) == bytes:
        return int.from_bytes(binary_data, "big")
    if type(binary_data) == BitArray or type(binary_data) == list:
        n = 0
        for i in range(len(binary_data)):
            n += binary_data[i] * 2 ** (len(binary_data) - i - 1)
        return n
    if type(binary_data) == list and len(binary_data) == 1 and type(binary_data[0]) == int:
        return binary_data[0]
