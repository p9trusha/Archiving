from bit_array import int_from_binary


def mtf(input_file_name, encode_file_name, m):
    input_file = open(input_file_name, "rb")
    s = input_file.read()
    input_file.close()
    t = list(range(2 ** m))
    len_symbol = m // 8 if m % 8 == 0 else m
    encode_file = open(encode_file_name, "wb")
    encode_file.write(m.to_bytes())
    for i in range(0, len(s), len_symbol):
        index = t.index(int_from_binary(s[i:i + len_symbol]))
        encode_file.write(index.to_bytes(len_symbol, "big"))
        t = [t[index]] + t[:index] + t[index+1:]
    encode_file.close()

# Обратное преобразование
def i_mtf(encode_file_name, decode_file_name):
    encode_file = open(encode_file_name, "rb")
    m = int_from_binary(encode_file.read(1))
    len_symbol = m // 8 if m % 8 == 0 else m
    s = encode_file.read()
    encode_file.close()
    t = list(range(2 ** m))
    decode_file = open(decode_file_name, "wb")
    for i in range(0, len(s), len_symbol):
        index = s[i]
        decode_file.write(t[index].to_bytes(len_symbol, "big"))
        t = [t[index]] + t[:index] + t[index + 1:]
    decode_file.close()
