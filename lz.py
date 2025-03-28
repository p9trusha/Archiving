from math import log2, ceil

from bit_array import BitArray, int_from_binary


def lz77(name_input_file, name_output_file):
    input_file = open(name_input_file, "rb")
    s = input_file.read()
    input_file.close()
    buffer_size_power = min(15, int(log2(len(s) * 8) - 1))
    buffer_size = 2 ** buffer_size_power - 1
    string_size_power = 4
    string_size = 2 ** string_size_power - 1
    coding_list = BitArray()
    n = len(s)
    i = 0
    while i < n:
        buffer = s[max(0,i - buffer_size) : i]
        new_buffer_size = len(buffer)
        shift = -1
        sub_s = b""
        for j in range(string_size, -1, -1):
            sub_s = s[i: min(i + j, n)]
            shift = buffer.rfind(sub_s)
            if shift != -1:
                break
        if len(sub_s) == 0:
            shift = new_buffer_size
        coding_list += BitArray(new_buffer_size - shift, mode="int", length=buffer_size_power)
        coding_list += BitArray(len(sub_s), mode="int", length=string_size_power)
        if i + len(sub_s) >= n:
            coding_list += BitArray(0, mode="int", length=8)
        else:
            coding_list += BitArray(s[i + len(sub_s)], mode="int", length=8)
        i += len(sub_s) + 1
    compressed_file = open(name_output_file, "wb")
    compressed_file.write(buffer_size_power.to_bytes())
    compressed_file.write(string_size_power.to_bytes())
    compressed_file.write(coding_list.to_bytearray())
    compressed_file.close()


# декодирование LZ77
def i_lz77(compressed_file_name, decompressed_file_name):
    compressed_file = open(compressed_file_name, "rb")
    s = compressed_file.read()
    compressed_file.close()
    buffer_size_power = s[0]
    string_size_power = s[1]
    s = s[2:]
    s = BitArray(s[1:], 'b')[:len(s) * 8 - s[0]]
    decompressed_s = bytearray()
    i = 0
    while i < len(s):
        shift = int_from_binary(s[i:i + buffer_size_power])
        i += buffer_size_power
        length = int_from_binary(s[i:i + string_size_power])
        i += string_size_power
        symbol = s[i:i + 8].to_bytearray(without_amount_of_extra_bits=True)
        i += 8
        n = len(decompressed_s)
        decompressed_s += decompressed_s[n - shift:n - shift + length] + symbol
    decompressed_s = decompressed_s[:-1]
    decompressed_file = open(decompressed_file_name, "wb")
    decompressed_file.write(decompressed_s)
    decompressed_file.close()


def lzw(name_input_file, compressed_file_name):
    input_file = open(name_input_file, "rb")
    s = input_file.read()
    input_file.close()
    dct = dict()
    for i in range(256):
        dct[i.to_bytes()] = i
    code_list = []
    start_i = 0
    while start_i < len(s):
        end_i = start_i + 1
        while s[start_i:end_i] in dct and end_i <= len(s):
            end_i += 1
        end_i -= 1
        if end_i != len(s):
            dct[s[start_i:end_i + 1]] = len(dct)
        code_list.append(dct[s[start_i:end_i]])
        start_i = max(end_i, start_i + 1)
    len_code = ceil(log2(len(dct)))
    encode_s = BitArray()
    for i in range(len(code_list)):
        encode_s += BitArray(code_list[i], mode="int", length=len_code)
    compressed_file = open(compressed_file_name, "wb")
    compressed_file.write(len_code.to_bytes())
    compressed_file.write(encode_s.to_bytearray())
    compressed_file.close()


def i_lzw(compressed_file_name, decompressed_file_name):
    compressed_file = open(compressed_file_name, "rb")
    s = compressed_file.read()
    compressed_file.close()
    len_code, s = s[0], s[1:]
    s = BitArray(s[1:], 'b')[:len(s) * 8 - s[0]]
    dct = {i: i.to_bytes() for i in range(256)}
    next_code = 256
    current_code = int_from_binary(s[0:len_code])
    decompressed_file = open(decompressed_file_name, "wb")
    decompressed_file.write(dct[current_code])
    previous = dct[current_code]
    for i in range(1, len(s) // len_code):
        code = int_from_binary(s[i * len_code:(i + 1) * len_code])
        if code in dct:
            current_str = dct[code]
        else:
            current_str = previous + previous[0].to_bytes()
        decompressed_file.write(current_str)
        dct[next_code] = previous + current_str[0].to_bytes()
        next_code += 1
        previous = current_str
    decompressed_file.close()

lzw("enwik7.txt", "lzw.txt")
i_lzw("lzw.txt", "i_lzw.txt")