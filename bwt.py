from math import ceil

from bit_array import BitArray
from bit_array import int_from_binary
from suffix_array2 import make_suffix_array
from suffix_array import make_suffix_array


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


def bwt(name_input_file, name_output_file, m):
    file_input = open(name_input_file, "rb")
    s = file_input.read()[:10 ** 5]
    file_input.close()
    n = len(s)
    if m % 8 != 0:
        s = BitArray(s, 'b')
        end = s[len(s) - (len(s) % m):]
    else:
        len_end = len(s) % (m // 8)
        end = s[len(s) - len_end:]
        s = s[:len(s) - len_end]
    file_output = open(name_output_file, mode="wb")
    file_output.write(len_end.to_bytes())
    s += s
    #sa = make_suffix_array(s, m)
    sa = make_suffix_array(s, m)
    len_symb = m // 8 if m % 8 == 0 else m
    bwm = list(filter(lambda x: x < len(sa) // 2, sa))
    s_index = bwm.index(0)
    if m % 8 != 0:
        file_output.write()
        last_column = BitArray()
        for i in range(len(bwm)):
            last_column += s[(bwm[i] - 1) % len(bwm) * len_symb:((bwm[i] - 1) % len(bwm) + 1) * len_symb]
        last_column += end
        file_output.write(last_column.to_bytearray())
    else:
        for i in range(len(bwm)):
            file_output.write(s[(bwm[i] - 1) % len(bwm) * len_symb:((bwm[i] - 1) % len(bwm) + 1) * len_symb])
        file_output.write(end)
    file_output.close()
    return s_index


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


def better_ibwt(s_index, compressed_file_name, decompressed_file_name, m):
    len_symb = m
    if m % 8 == 0:
        len_symb = m // 8
    compressed_file = open(compressed_file_name, "rb")
    last_column = compressed_file.read()
    len_end = last_column[0]
    end = last_column[len(last_column) - len_end:]
    print(end)
    last_column = last_column[1:len(last_column) - len_end]
    print(len(last_column))
    compressed_file.close()
    n = len(last_column) // len_symb
    p_inverse = counting_sort_arg(last_column, m, len_symb)
    decompressed_file = open(decompressed_file_name, "wb")
    j = s_index
    for _ in range(n):
        j = p_inverse[j]
        decompressed_file.write(last_column[j * len_symb:(j + 1) * len_symb])
    decompressed_file.write(end)
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
