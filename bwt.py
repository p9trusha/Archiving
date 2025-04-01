from math import ceil, log2

from bit_array import BitArray
from bit_array import int_from_binary
from suffix_array2 import make_suffix_array


# def BWT(name_input_file, name_output_file):
#     # T(n)=O(n^2*log(n)) S(n)= O(n^2)
#     file_input = open(name_input_file, "rb")
#     S = file_input.read()
#     file_input.close()
#     N = len(S)
#     BWM = [S[i:] + S[0:i] for i in range(N)]
#     BWM.sort()
#     # [print(i,BWM[i]) for i in range(N)]
#     # int_from_binary(compressed_s[i:i + 8]("".join([BWM[i][-1] for i in range(N)]))
#     file_output = open(name_output_file, mode="wb")
#     for i in range(N):
#         file_output.write(BWM[i][-1].to_bytes())
#     S_index = BWM.index(S)
#     return S_index


def bwt(name_input_file, name_output_file, m, block_size_power=7):
    file_input = open(name_input_file, "rb")
    s = file_input.read()
    file_input.close()
    n = len(s)
    len_over = 0
    if m % 8 != 0:
        s = BitArray(s, 'b')
        over = s[len(s) - (len(s) % m):]
    else:
        len_over = len(s) % (m // 8)
        over = s[:len_over]
        s = s[len_over:]
    file_output = open(name_output_file, mode="wb")
    file_output.write(m.to_bytes())
    file_output.write(len_over.to_bytes())
    file_output.write(over)
    file_output.write(block_size_power.to_bytes())
    block_size = 10 ** block_size_power
    for j in range(ceil(len(s) / block_size)):
        block = s[j * block_size:(j + 1) * block_size]
        block += block
        #sa = make_suffix_array(s, m)
        sa = make_suffix_array(block, m)
        len_symbol = m // 8 if m % 8 == 0 else m
        bwm = list(filter(lambda x: x < len(sa) // 2, sa))
        s_index = bwm.index(0)
        if m % 8 == 0:
            len_s_index = ceil(ceil(log2(s_index + 1)) / 8)
            file_output.write(len_s_index.to_bytes())
            file_output.write(s_index.to_bytes(length=len_s_index))
            for j in range(len(bwm)):
                file_output.write(block[(bwm[j] - 1) % len(bwm) * len_symbol:
                                        ((bwm[j] - 1) % len(bwm) + 1) * len_symbol])
        else:
            last_column = BitArray()
            for j in range(len(bwm)):
                last_column += s[(bwm[j] - 1) % len(bwm) * len_symbol:((bwm[j] - 1) % len(bwm) + 1) * len_symbol]
            last_column += over
            file_output.write(last_column.to_bytearray())
    file_output.close()


def bwt2(name_input_file, name_output_file):
    file_input = open(name_input_file, "rb")
    s = file_input.read()[:10 ** 4]
    file_input.close()
    n = len(s)
    m = 8
    file_output = open(name_output_file, mode="wb")
    s_index = suffix_array(s, list(range(n)), [[] for _ in range(2 ** m)], 0, file_output)
    file_output.close()
    return s_index


def ibwt(last_colum, s_index):
    n = len(last_colum)
    bwm = ["" for i in range(n)]
    for i in range(n):
        for j in range(n):
            bwm[j] = last_colum[j] + bwm[j]
        bwm.sort()
    s = bwm[s_index]
    return s


def better_i_bwt(compressed_file_name, decompressed_file_name):
    compressed_file = open(compressed_file_name, "rb")
    m = int_from_binary(compressed_file.read(1))
    len_symbol = m
    if m % 8 == 0:
        len_symbol = m // 8
    len_over = int_from_binary(compressed_file.read(1))
    over = compressed_file.read(len_over)
    block_size_power = int_from_binary(compressed_file.read(1))
    s = compressed_file.read()
    compressed_file.close()
    block_size = 10 ** block_size_power
    i = 0
    decompressed_file = open(decompressed_file_name, "wb")
    decompressed_file.write(over)
    while i < len(s):
        len_s_index = s[i]
        i += 1
        s_index = int_from_binary(s[i:i + len_s_index])
        i += len_s_index
        last_column = s[i:i + block_size]
        i += block_size
        p_inverse = counting_sort_arg(last_column, m, len_symbol)
        j = s_index
        n = len(last_column) // len_symbol
        for _ in range(n):
            j = p_inverse[j]
            decompressed_file.write(last_column[j * len_symbol:(j + 1) * len_symbol])
    decompressed_file.close()


def counting_sort_arg(s, m, len_symb):
    n = len(s) // len_symb
    t = {}
    # for i in range(n):
    #     t[int_from_binary(s[i * len_symb:(i + 1) * len_symb])] += 1
    for i in range(n):
        key = int_from_binary(s[i * len_symb:(i + 1) * len_symb])
        if key in t:
            t[key] += 1
        else:
            t[key] = 1
    index = 0
    t2 = {}
    for key in sorted(t.keys()):
        t2[key] = index
        index += t[key]
    # for j in range(1, len_tab):
    #     t2[j] = t2[j - 1] + t[j - 1]
    p_inverse = [-1 for _ in range(n)]
    for i in range(n):
        p_inverse[t2[int_from_binary(s[i * len_symb:(i + 1) * len_symb])]] = i
        #p[i] = t2[ord(arr[i])]
        t2[int_from_binary(s[i * len_symb:(i + 1) * len_symb])] += 1
    return p_inverse
