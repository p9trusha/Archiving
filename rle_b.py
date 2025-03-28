from math import ceil

from bit_array import BitArray, int_from_binary


def rle(name_input_file, name_output_file, m=8):
    file_input = open(name_input_file, "rb")
    file_output = open(name_output_file, "wb")
    S = file_input.read()
    len_symb = m // 8 if m % 8 == 0 else m
    file_input.close()
    encode_s = b''
    if m % 8 != 0:
        S = BitArray(S, 'b')
        S += [False] * len_symb
        encode_s = BitArray()
    else:
        S += (0).to_bytes(length=len_symb)
    prev_symb = S[0:len_symb]
    counter = 1
    flag = False
    start_i = 0
    for i in range(len_symb, len(S), len_symb):
        symb = S[i:i + len_symb]
        if prev_symb == symb:
            if flag:
                count = 128 + (i - start_i) // len_symb - 1
                if m % 8 == 0:
                    count = count.to_bytes()
                encode_s += count
                encode_s += S[start_i:i - len_symb]
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
                    start_i = i - len_symb
                    flag = True
                elif (i - start_i) // len_symb == 127:
                    count = 255
                    if m % 8 == 0:
                        count = count.to_bytes()
                    encode_s += count
                    encode_s += S[start_i:i]
                    flag = False
            else:
                if m % 8 == 0:
                    counter = counter.to_bytes()
                encode_s += counter
                encode_s += prev_symb
                counter = 1
        prev_symb = symb
    if flag:
        count = 128 + ceil((len(S) - start_i) / len_symb)
        if m % 8 == 0:
            count = count.to_bytes()
        encode_s += count
        encode_s += S[start_i:len(S) - len_symb]
    if m % 8 != 0 :
        encode_s = bytes(encode_s)
    file_output.write(encode_s)
    file_output.close()


def i_rle(compressed_file_name, decompressed_file_name, m=8):
    len_symb = m // 8 if m % 8 == 0 else m
    compressed_file = open(compressed_file_name, "rb")
    decompressed_file = open(decompressed_file_name, "wb")
    compressed_S = compressed_file.read()
    compressed_file.close()
    if m % 8 != 0:
        compressed_S = BitArray(compressed_S, 'b')
        i_rle_bits(compressed_S, len_symb, decompressed_file)
    else:
        N = len(compressed_S)
        i = 0
        while i < N:
            if compressed_S[i] < 128:
                decompressed_file.write(compressed_S[i] * compressed_S[i + 1:i + 1 + len_symb])
                i += 1 + len_symb
            else:
                decompressed_file.write(compressed_S[i + 1:i + 1 + len_symb * (compressed_S[i] - 128)])
                i += len_symb * (compressed_S[i] - 128) + 1
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
