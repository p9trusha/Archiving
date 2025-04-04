from math import ceil

from bit_array import BitArray, int_from_binary


def rle(name_input_file, name_output_file, m):
    file_input = open(name_input_file, "rb")
    file_output = open(name_output_file, "wb")
    s = file_input.read()
    len_symbol = m // 8 if m % 8 == 0 else m
    file_input.close()
    encode_s = bytearray()
    len_over = 0
    over = b""
    if m % 8 != 0:
        s = BitArray(s, 'b')
        s += [False] * len_symbol
        encode_s = BitArray()
    else:
        len_over = len(s) % len_symbol
        over = s[:len_over]
        s = s[len_over:]
        s += (0).to_bytes(length=len_symbol)
    prev_symb = s[0:len_symbol]
    counter = 1
    flag = False
    start_i = 0
    for i in range(len_symbol, len(s), len_symbol):
        symb = s[i:i + len_symbol]
        if prev_symb == symb:
            if flag:
                count = 128 + (i - start_i) // len_symbol - 1
                if m % 8 == 0:
                    count = count.to_bytes()
                encode_s += count
                encode_s += s[start_i:i - len_symbol]
                flag = False
            if counter == 127:
                if m % 8 == 0:
                    counter = counter.to_bytes()
                encode_s += counter
                encode_s += prev_symb
                counter = 0
            counter += 1
        else:
            if counter == 1:
                if not flag:
                    start_i = i - len_symbol
                    flag = True
                elif (i - start_i) // len_symbol == 127:
                    count = 255
                    if m % 8 == 0:
                        count = count.to_bytes()
                    encode_s += count
                    encode_s += s[start_i:i]
                    flag = False
            else:
                if m % 8 == 0:
                    counter = counter.to_bytes()
                encode_s += counter
                encode_s += prev_symb
                counter = 1
        prev_symb = symb
    if flag:
        count = 128 + ceil((len(s) - start_i) / len_symbol)
        if m % 8 == 0:
            count = count.to_bytes()
        encode_s += count
        encode_s += s[start_i:-len_symbol]
    if m % 8 != 0:
        encode_s = bytes(encode_s)
    file_output.write(m.to_bytes())
    file_output.write(len_over.to_bytes())
    file_output.write(over)
    file_output.write(encode_s)
    file_output.close()


def i_rle(compressed_file_name, decompressed_file_name):
    compressed_file = open(compressed_file_name, "rb")
    m = int_from_binary(compressed_file.read(1))
    len_over = int_from_binary(compressed_file.read(1))
    over = compressed_file.read(len_over)
    len_symbol = m // 8 if m % 8 == 0 else m
    decompressed_file = open(decompressed_file_name, "wb")
    decompressed_file.write(over)
    compressed_s = compressed_file.read()
    compressed_file.close()
    if m % 8 != 0:
        compressed_s = BitArray(compressed_s, 'b')
        i_rle_bits(compressed_s, len_symbol, decompressed_file)
    else:
        N = len(compressed_s)
        i = 0
        while i < N:
            if compressed_s[i] < 128:
                decompressed_file.write(compressed_s[i] * compressed_s[i + 1:i + 1 + len_symbol])
                i += 1 + len_symbol
            else:
                decompressed_file.write(compressed_s[i + 1:i + 1 + len_symbol * (compressed_s[i] - 128)])
                i += len_symbol * (compressed_s[i] - 128) + 1
    decompressed_file.close()
    # print(open("enwik7.txt", "rb").read() == open("decode_text.txt", "rb").read())


def i_rle_bits(compressed_s, len_symb, decompressed_file):
    n = len(compressed_s)
    decode_s = BitArray()
    i = 0
    while i < n:
        if int_from_binary(compressed_s[i:i + 8]) < 128:
            decode_s += compressed_s[i + 8:i + 8 + len_symb] * int_from_binary(compressed_s[i:i + 8])
            #print(compressed_s[i + 8:i + 8 + len_symb])
            i += 8 + len_symb
        else:
            decode_s += compressed_s[i + 8:
                                     i + 8 + len_symb * (int_from_binary(compressed_s[i:i + 8]) - 128)]
            i += len_symb * (int_from_binary(compressed_s[i:i + 8]) - 128) + 8
    decompressed_file.write(decode_s.to_bytearray())
